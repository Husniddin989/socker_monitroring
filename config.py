import json
import logging
import os

class ConfigManager:
    def __init__(self, config_file='config.json'):
        self.config_file = config_file
        self.config = self.load_config()
        
    def load_config(self):
        """Config faylni yuklash"""
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                logging.info("Config yuklandi")
                return config
        except FileNotFoundError:
            logging.error(f"Config fayl topilmadi: {self.config_file}")
            return self.get_default_config()
    
    def reload_config(self):
        """Config faylni qayta yuklash"""
        self.config = self.load_config()
    
    def get_default_config(self):
        """Default config"""
        return {
            "telegram": {
                "bot_token": "7120243579:AAEoaMz5DK8pv1uvwmbD--Mmt8nqbhL_mec",
                "chat_id": "-1001686130633"
            },
            "thresholds": {
                "cpu_percent": 90,
                "memory_percent": 85,
                "disk_percent": 90
            },
            "check_interval": 5,
            "alert_cooldown": 300,
            "top_processes": 30
        }
    
    def create_default_config(self):
        """Default config faylni yaratish"""
        config = self.get_default_config()
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=4)
        print(f"{self.config_file} yaratildi. Telegram ma'lumotlarini kiriting.")
    
    def get(self, key, default=None):
        """Config qiymatini olish"""
        keys = key.split('.')
        value = self.config
        for k in keys:
            value = value.get(k, default)
            if value is None:
                return default
        return value