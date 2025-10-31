#!/usr/bin/env python3
"""
Server Monitoring Tool with Unix Socket
Real-time monitoring + Telegram alerts
"""

import logging
import time
import os
import sys
import socket as sock
import json
import threading

from config import ConfigManager
from telegram_notifier import TelegramNotifier

# Logging sozlash
from logging_config import setup_monitoring_logging
setup_monitoring_logging()

class SocketMonitoringIntegration:
    """Unix Socket orqali monitoring ma'lumotlarini olish va alert yuborish"""
    
    def __init__(self, config_file='config.json', socket_path='/tmp/monitor.sock'):
        self.config = ConfigManager(config_file)
        self.socket_path = socket_path
        
        # Telegram notifier
        bot_token = self.config.get('telegram.bot_token')
        chat_id = self.config.get('telegram.chat_id')
        
        if not bot_token or not chat_id or bot_token == 'YOUR_BOT_TOKEN':
            logging.error("❌ Telegram bot_token va chat_id to'ldirilmagan!")
            sys.exit(1)
        
        self.notifier = TelegramNotifier(bot_token, chat_id)
        
        # Alert tracking
        self.last_alerts = {
            'cpu': 0,
            'memory': 0,
            'disk': 0
        }
        
        self.running = False
        self.client_socket = None
    
    def connect_to_socket(self):
        """Socket serverga ulanish"""
        if not os.path.exists(self.socket_path):
            logging.error(f"❌ Socket topilmadi: {self.socket_path}")
            logging.error("Avval socket_server.py ni ishga tushiring!")
            return False
        
        try:
            self.client_socket = sock.socket(sock.AF_UNIX, sock.SOCK_STREAM)
            self.client_socket.connect(self.socket_path)
            logging.info(f"✅ Socket serverga ulandi: {self.socket_path}")
            return True
        except Exception as e:
            logging.error(f"❌ Socket ulanishda xato: {e}")
            return False
    
    def start(self):
        """Monitoring boshlash"""
        logging.info("=" * 60)
        logging.info("🚀 Socket-based Monitoring ishga tushmoqda...")
        logging.info("=" * 60)
        
        if not self.connect_to_socket():
            return
        
        self.running = True
        
        # Startup message
        self._send_startup_message()
        
        try:
            buffer = ""
            while self.running:
                # Socket'dan ma'lumot olish
                chunk = self.client_socket.recv(4096).decode('utf-8')
                if not chunk:
                    logging.error("❌ Socket bilan aloqa uzildi")
                    break
                
                buffer += chunk
                
                # Yangi qatorni topish
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    try:
                        data = json.loads(line)
                        self._process_metrics(data)
                    except json.JSONDecodeError:
                        pass
                
        except KeyboardInterrupt:
            self.stop()
        except Exception as e:
            logging.error(f"❌ Monitoring xatosi: {e}")
            self.stop()
    
    def stop(self):
        """Monitoring to'xtatish"""
        logging.info("\n" + "=" * 60)
        logging.info("⛔ Monitoring to'xtatilmoqda...")
        logging.info("=" * 60)
        
        self.running = False
        
        if self.client_socket:
            self.client_socket.close()
        
        self._send_stop_message()
        logging.info("✅ Monitoring to'xtatildi")
    
    def _process_metrics(self, data):
        """Metrikalarni tekshirish va alert yuborish"""
        # Config qayta yuklash
        self.config.reload_config()
        
        cpu = data['cpu']
        memory = data['memory']
        disk = data['disk']
        
        # Thresholds
        cpu_threshold = self.config.get('thresholds.cpu_percent', 90)
        memory_threshold = self.config.get('thresholds.memory_percent', 85)
        disk_threshold = self.config.get('thresholds.disk_percent', 90)
        
        # CPU check
        if cpu > cpu_threshold and self._should_send_alert('cpu'):
            self._send_cpu_alert(data, cpu_threshold)
        
        # Memory check
        if memory > memory_threshold and self._should_send_alert('memory'):
            self._send_memory_alert(data, memory_threshold)
        
        # Disk check
        if disk > disk_threshold and self._should_send_alert('disk'):
            self._send_disk_alert(data, disk_threshold)
    
    def _should_send_alert(self, alert_type):
        """Alert yuborish kerakmi?"""
        cooldown = self.config.get('alert_cooldown', 300)
        current_time = time.time()
        time_passed = current_time - self.last_alerts[alert_type]
        
        if time_passed > cooldown:
            return True
        else:
            remaining = int(cooldown - time_passed)
            logging.debug(f"⏳ {alert_type} alert kutilmoqda: {remaining}s qoldi")
            return False
    
    def _send_cpu_alert(self, data, threshold):
        """CPU alert"""
        from datetime import datetime
        
        hostname = sock.gethostname()
        ip = self._get_ip_address()
        uptime = self._get_uptime()
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        alert_data = {
            'emoji': '🚨',
            'title': 'CPU ALERT',
            'date': now,
            'hostname': hostname,
            'ip': ip,
            'uptime': uptime,
            'metrics': [
                f"💻 CPU Usage: {data['cpu']:.1f}% of 100%",
                f"⚠️ Threshold: {threshold}%"
            ],
            'process_title': f"Top {len(data['top_cpu_processes'])} CPU-Consuming Processes:",
            'processes': []
        }
        
        for i, proc in enumerate(data['top_cpu_processes'], 1):
            name = proc['name'][:20]
            cpu_val = f"{proc['cpu']:.1f}%"
            alert_data['processes'].append(f"{i:<2}. {name:<20} {cpu_val:>7}")
        
        if self.notifier.send_formatted_alert(alert_data):
            self.last_alerts['cpu'] = time.time()
            logging.warning(f"🔴 CPU alert yuborildi: {data['cpu']:.1f}%")
    
    def _send_memory_alert(self, data, threshold):
        """Memory alert"""
        from datetime import datetime
        
        hostname = sock.gethostname()
        ip = self._get_ip_address()
        uptime = self._get_uptime()
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        alert_data = {
            'emoji': '🚨',
            'title': 'Memory ALERT',
            'date': now,
            'hostname': hostname,
            'ip': ip,
            'uptime': uptime,
            'metrics': [
                f"💾 Memory: {data['memory']:.1f}% of {data['memory_total_gb']}G",
                f"⚠️ Threshold: {threshold}%",
                f"📊 Used: {data['memory_used_gb']}G"
            ],
            'process_title': f"Top {len(data['top_memory_processes'])} Memory-Consuming Processes:",
            'processes': []
        }
        
        for i, proc in enumerate(data['top_memory_processes'], 1):
            name = proc['name'][:20]
            mem_mb = proc['memory_mb']
            mem_val = f"{mem_mb:.0f}M" if mem_mb < 1024 else f"{mem_mb/1024:.1f}G"
            alert_data['processes'].append(f"{i:<2}. {name:<20} {mem_val:>7}")
        
        if self.notifier.send_formatted_alert(alert_data):
            self.last_alerts['memory'] = time.time()
            logging.warning(f"🟡 Memory alert yuborildi: {data['memory']:.1f}%")
    
    def _send_disk_alert(self, data, threshold):
        """Disk alert"""
        from datetime import datetime
        
        hostname = sock.gethostname()
        ip = self._get_ip_address()
        uptime = self._get_uptime()
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        alert_data = {
            'emoji': '🚨',
            'title': 'Disk ALERT',
            'date': now,
            'hostname': hostname,
            'ip': ip,
            'uptime': uptime,
            'metrics': [
                f"💾 Disk: {data['disk']:.1f}% of {data['disk_total_gb']}G",
                f"⚠️ Threshold: {threshold}%",
                f"📊 Used: {data['disk_used_gb']}G"
            ],
            'processes': []
        }
        
        if self.notifier.send_formatted_alert(alert_data):
            self.last_alerts['disk'] = time.time()
            logging.warning(f"💾 Disk alert yuborildi: {data['disk']:.1f}%")
    
    def _get_ip_address(self):
        """IP manzil"""
        try:
            s = sock.socket(sock.AF_INET, sock.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "N/A"
    
    def _get_uptime(self):
        """Uptime"""
        import psutil
        boot_time = psutil.boot_time()
        uptime_seconds = time.time() - boot_time
        hours = int(uptime_seconds // 3600)
        minutes = int((uptime_seconds % 3600) // 60)
        return f"{hours}h {minutes}m"
    
    def _send_startup_message(self):
        """Boshlang'ich xabar"""
        from datetime import datetime
        
        hostname = sock.gethostname()
        ip = self._get_ip_address()
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        message = "┌────────────────────────────────────────────┐\n"
        message += "│    ✅ Socket Monitoring Started           │\n"
        message += "├────────────────────────────────────────────┤\n"
        message += f"│🗓️ Date: {now:<30}│\n"
        message += f"│🖥️ Hostname: {hostname:<30}│\n"
        message += f"│🌐 IP Address: {ip:<28}│\n"
        message += "├────────────────────────────────────────────┤\n"
        message += f"│💻 CPU Threshold: {self.config.get('thresholds.cpu_percent', 90)}%{' '*(25-len(str(self.config.get('thresholds.cpu_percent', 90))))}│\n"
        message += f"│💾 RAM Threshold: {self.config.get('thresholds.memory_percent', 85)}%{' '*(25-len(str(self.config.get('thresholds.memory_percent', 85))))}│\n"
        message += f"│💾 Disk Threshold: {self.config.get('thresholds.disk_percent', 90)}%{' '*(24-len(str(self.config.get('thresholds.disk_percent', 90))))}│\n"
        message += "├────────────────────────────────────────────┤\n"
        message += "│🔌 Mode: Unix Socket (Real-time)          │\n"
        message += "└────────────────────────────────────────────┘"
        
        self.notifier.send_message(f"<pre>{message}</pre>")
    
    def _send_stop_message(self):
        """To'xtatish xabari"""
        from datetime import datetime
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        message = "┌────────────────────────────────────────────┐\n"
        message += "│          ⛔ Monitoring Stopped            │\n"
        message += "├────────────────────────────────────────────┤\n"
        message += f"│🗓️ Date: {now:<30}│\n"
        message += "└────────────────────────────────────────────┘"
        
        self.notifier.send_message(f"<pre>{message}</pre>")


def main():
    """Dasturni ishga tushirish"""
    config_file = 'config.json'
    
    # Config fayl mavjudligini tekshirish
    if not os.path.exists(config_file):
        logging.info(f"Config fayl topilmadi. {config_file} yaratilmoqda...")
        config_manager = ConfigManager(config_file)
        config_manager.create_default_config()
        logging.info("✅ Config fayl yaratildi!")
        logging.info("📝 Config.json faylida Telegram ma'lumotlarini to'ldiring")
        return
    
    # Monitoring boshlash
    monitor = SocketMonitoringIntegration(config_file)
    monitor.start()


if __name__ == "__main__":
    main()