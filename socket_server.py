#!/usr/bin/env python3
"""
Unix Socket Server - Real-time process monitoring
"""

import socket
import os
import json
import threading
import logging
import psutil
import time

class MonitoringSocketServer:
    def __init__(self, socket_path='/tmp/monitor.sock'):
        self.socket_path = socket_path
        self.server_socket = None
        self.running = False
        self.clients = []
        self.lock = threading.Lock()
        
        # Monitoring data
        self.current_metrics = {
            'cpu': 0,
            'memory': 0,
            'disk': 0,
            'top_cpu_processes': [],
            'top_memory_processes': [],
            'timestamp': 0
        }
        
    def start(self):
        """Server boshlash"""
        # Eski socket faylni o'chirish
        if os.path.exists(self.socket_path):
            os.unlink(self.socket_path)
        
        # Unix socket yaratish
        self.server_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.server_socket.bind(self.socket_path)
        self.server_socket.listen(5)
        
        # Permissions o'rnatish
        os.chmod(self.socket_path, 0o666)
        
        self.running = True
        logging.info(f"🚀 Socket server ishga tushdi: {self.socket_path}")
        
        # Monitoring thread
        monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        monitor_thread.start()
        
        # Client handler thread
        accept_thread = threading.Thread(target=self._accept_clients, daemon=True)
        accept_thread.start()
        
    def stop(self):
        """Server to'xtatish"""
        self.running = False
        
        # Barcha clientlarni yopish
        with self.lock:
            for client in self.clients:
                try:
                    client.close()
                except:
                    pass
            self.clients.clear()
        
        # Socket yopish
        if self.server_socket:
            self.server_socket.close()
        
        # Socket faylni o'chirish
        if os.path.exists(self.socket_path):
            os.unlink(self.socket_path)
        
        logging.info("⛔ Socket server to'xtatildi")
    
    def _accept_clients(self):
        """Clientlarni qabul qilish"""
        while self.running:
            try:
                client_socket, _ = self.server_socket.accept()
                logging.info(f"✅ Yangi client ulandi")
                
                with self.lock:
                    self.clients.append(client_socket)
                
                # Client handler thread
                client_thread = threading.Thread(
                    target=self._handle_client,
                    args=(client_socket,),
                    daemon=True
                )
                client_thread.start()
                
            except Exception as e:
                if self.running:
                    logging.error(f"Client qabul qilishda xato: {e}")
    
    def _handle_client(self, client_socket):
        """Client bilan ishlash"""
        try:
            while self.running:
                # Ma'lumot yuborish
                data = json.dumps(self.current_metrics) + '\n'
                client_socket.sendall(data.encode('utf-8'))
                time.sleep(1)  # Har sekundda yangilanish
                
        except (BrokenPipeError, ConnectionResetError):
            logging.info("Client uzildi")
        except Exception as e:
            logging.error(f"Client bilan ishlashda xato: {e}")
        finally:
            with self.lock:
                if client_socket in self.clients:
                    self.clients.remove(client_socket)
            try:
                client_socket.close()
            except:
                pass
    
    def _monitor_loop(self):
        """Monitoring sikli"""
        # Minimal logging - har 60 sekundda bir marta
        last_log_time = 0
        
        while self.running:
            try:
                # CPU
                cpu_percent = psutil.cpu_percent(interval=1)
                
                # Memory
                memory = psutil.virtual_memory()
                
                # Disk
                disk = psutil.disk_usage('/')
                
                # Top CPU processes
                top_cpu = self._get_top_cpu_processes(5)
                
                # Top Memory processes
                top_memory = self._get_top_memory_processes(5)
                
                # Ma'lumotlarni yangilash
                self.current_metrics = {
                    'cpu': round(cpu_percent, 1),
                    'memory': round(memory.percent, 1),
                    'disk': round(disk.percent, 1),
                    'memory_total_gb': round(memory.total / (1024**3), 1),
                    'memory_used_gb': round(memory.used / (1024**3), 1),
                    'disk_total_gb': round(disk.total / (1024**3), 1),
                    'disk_used_gb': round(disk.used / (1024**3), 1),
                    'top_cpu_processes': top_cpu,
                    'top_memory_processes': top_memory,
                    'timestamp': time.time()
                }
                
                # Har 60 sekundda bir marta log
                current_time = time.time()
                if current_time - last_log_time > 60:
                    logging.info(f"📊 CPU: {cpu_percent:.1f}% | RAM: {memory.percent:.1f}% | Disk: {disk.percent:.1f}% | Clients: {len(self.clients)}")
                    last_log_time = current_time
                
            except Exception as e:
                logging.error(f"Monitoring xatosi: {e}")
                time.sleep(1)
    
    def _get_top_cpu_processes(self, limit=5):
        """Top CPU processes"""
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
            try:
                proc.cpu_percent(interval=0.1)
            except:
                pass
        
        time.sleep(0.5)
        
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
            try:
                pinfo = proc.info
                if pinfo['cpu_percent'] and pinfo['cpu_percent'] > 0:
                    processes.append({
                        'pid': pinfo['pid'],
                        'name': pinfo['name'],
                        'cpu': round(pinfo['cpu_percent'], 1)
                    })
            except:
                pass
        
        return sorted(processes, key=lambda x: x['cpu'], reverse=True)[:limit]
    
    def _get_top_memory_processes(self, limit=5):
        """Top Memory processes"""
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
            try:
                pinfo = proc.info
                mem_info = pinfo.get('memory_info')
                if mem_info:
                    mem_mb = mem_info.rss / (1024 * 1024)
                    processes.append({
                        'pid': pinfo['pid'],
                        'name': pinfo['name'],
                        'memory_mb': round(mem_mb, 1)
                    })
            except:
                pass
        
        return sorted(processes, key=lambda x: x['memory_mb'], reverse=True)[:limit]


if __name__ == "__main__":
    from logging_config import setup_socket_server_logging
    setup_socket_server_logging()
    
    server = MonitoringSocketServer()
    
    try:
        server.start()
        logging.info("Server ishlayapti... Ctrl+C tugmasini bosing to'xtatish uchun")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("\nTo'xtatilmoqda...")
        server.stop()