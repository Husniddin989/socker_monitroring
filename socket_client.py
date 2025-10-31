#!/usr/bin/env python3
"""
Unix Socket Client - Real-time monitoring dashboard
"""

import socket
import json
import sys
import os

class MonitoringClient:
    def __init__(self, socket_path='/tmp/monitor.sock'):
        self.socket_path = socket_path
        self.client_socket = None
        
    def connect(self):
        """Serverga ulanish"""
        if not os.path.exists(self.socket_path):
            print(f"❌ Socket topilmadi: {self.socket_path}")
            print("Avval socket_server.py ni ishga tushiring!")
            return False
        
        try:
            self.client_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.client_socket.connect(self.socket_path)
            print(f"✅ Serverga ulandi: {self.socket_path}")
            return True
        except Exception as e:
            print(f"❌ Ulanishda xato: {e}")
            return False
    
    def disconnect(self):
        """Serverdan uzilish"""
        if self.client_socket:
            self.client_socket.close()
    
    def receive_data(self):
        """Ma'lumot olish"""
        try:
            buffer = ""
            while True:
                chunk = self.client_socket.recv(4096).decode('utf-8')
                if not chunk:
                    return None
                
                buffer += chunk
                if '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    return json.loads(line)
        except Exception as e:
            print(f"❌ Ma'lumot olishda xato: {e}")
            return None
    
    def display_dashboard(self, data):
        """Dashboard ko'rsatish"""
        # Clear screen
        os.system('clear' if os.name == 'posix' else 'cls')
        
        print("=" * 80)
        print("🖥️  REAL-TIME SERVER MONITORING DASHBOARD".center(80))
        print("=" * 80)
        print()
        
        # System metrics
        print("📊 SYSTEM METRICS:")
        print("-" * 80)
        print(f"  💻 CPU Usage:     {data['cpu']:>6.1f}%  {'█' * int(data['cpu'] / 2)}")
        print(f"  💾 Memory Usage:  {data['memory']:>6.1f}%  {'█' * int(data['memory'] / 2)}")
        print(f"     Total: {data['memory_total_gb']:.1f}G | Used: {data['memory_used_gb']:.1f}G")
        print(f"  💾 Disk Usage:    {data['disk']:>6.1f}%  {'█' * int(data['disk'] / 2)}")
        print(f"     Total: {data['disk_total_gb']:.1f}G | Used: {data['disk_used_gb']:.1f}G")
        print()
        
        # Top CPU processes
        print("🔥 TOP CPU PROCESSES:")
        print("-" * 80)
        if data['top_cpu_processes']:
            for i, proc in enumerate(data['top_cpu_processes'], 1):
                print(f"  {i}. {proc['name'][:30]:<30} | PID: {proc['pid']:<8} | CPU: {proc['cpu']:>5.1f}%")
        else:
            print("  No active processes")
        print()
        
        # Top Memory processes
        print("💾 TOP MEMORY PROCESSES:")
        print("-" * 80)
        if data['top_memory_processes']:
            for i, proc in enumerate(data['top_memory_processes'], 1):
                mem_str = f"{proc['memory_mb']:.0f}M" if proc['memory_mb'] < 1024 else f"{proc['memory_mb']/1024:.1f}G"
                print(f"  {i}. {proc['name'][:30]:<30} | PID: {proc['pid']:<8} | MEM: {mem_str:>7}")
        else:
            print("  No active processes")
        print()
        
        print("=" * 80)
        print("Press Ctrl+C to exit".center(80))
        print("=" * 80)
    
    def run(self):
        """Clientni ishga tushirish"""
        if not self.connect():
            return
        
        try:
            while True:
                data = self.receive_data()
                if data:
                    self.display_dashboard(data)
                else:
                    print("❌ Server bilan aloqa uzildi")
                    break
        except KeyboardInterrupt:
            print("\n\n✅ Client to'xtatildi")
        finally:
            self.disconnect()


if __name__ == "__main__":
    client = MonitoringClient()
    client.run()