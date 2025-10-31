import requests
import logging

class TelegramNotifier:
    def __init__(self, bot_token, chat_id):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    def send_message(self, message):
        """Telegram orqali xabar yuborish"""
        data = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "HTML"
        }
        
        try:
            response = requests.post(self.url, data=data, timeout=10)
            if response.status_code == 200:
                logging.info("✅ Telegram xabar yuborildi")
                return True
            else:
                logging.error(f"❌ Telegram xato: {response.text}")
                return False
        except Exception as e:
            logging.error(f"❌ Telegram API xatosi: {e}")
            return False
    
    def send_formatted_alert(self, alert_data):
        """Formatlangan alert yuborish"""
        message = self._format_alert(alert_data)
        return self.send_message(f"<pre>{message}</pre>")
    
    def _format_alert(self, data):
        """Alert formatlash"""
        message = "┌────────────────────────────────────────────┐\n"
        message += f"│         {data['emoji']} {data['title']:<30}│\n"
        message += "├────────────────────────────────────────────┤\n"
        message += f"│🗓️ Date: {data['date']:<30}.       │\n"
        message += f"│🖥️ Hostname: {data['hostname']:<30}│\n"
        message += f"│🌐 IP Address: {data['ip']:<28}.   │\n"
        message += f"│⏳ Uptime: {data['uptime']:<32}.   │\n"
        message += "├────────────────────────────────────────────┤\n"
        
        # Metrika ma'lumotlari
        for line in data['metrics']:
            message += f"│{line:<44}│\n"
        
        message += "├────────────────────────────────────────────┤\n"
        
        # Top processes
        if 'processes' in data:
            message += f"│📊 {data['process_title']:<42}│\n"
            for proc in data['processes']:
                message += f"│  {proc:<42}│\n"
        
        message += "└────────────────────────────────────────────┘"
        return message