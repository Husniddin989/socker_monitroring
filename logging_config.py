import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
import os

def setup_logging(log_level=logging.INFO, use_rotation=True):
    """
    Logging setup with automatic rotation
    
    Args:
        log_level: Logging level (INFO, WARNING, ERROR)
        use_rotation: True - rotating by size, False - daily rotation
    """
    
    # Log directory
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Root logger
    logger = logging.getLogger()
    logger.setLevel(log_level)
    
    # Clear existing handlers
    logger.handlers.clear()
    
    if use_rotation:
        # Rotating by size (10MB max, keep 5 files)
        file_handler = RotatingFileHandler(
            os.path.join(log_dir, 'monitor.log'),
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5,              # 5 ta backup
            encoding='utf-8'
        )
    else:
        # Daily rotation (keep 7 days)
        file_handler = TimedRotatingFileHandler(
            os.path.join(log_dir, 'monitor.log'),
            when='midnight',            # Har kecha yarim tunda yangi fayl
            interval=1,                 # Har 1 kun
            backupCount=7,              # 7 kunlik log
            encoding='utf-8'
        )
    
    file_handler.setFormatter(formatter)
    file_handler.setLevel(log_level)
    logger.addHandler(file_handler)
    
    # Console handler - faqat WARNING va yuqori
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.WARNING)  # Faqat muhim xabarlar
    logger.addHandler(console_handler)
    
    return logger


def setup_socket_server_logging():
    """Socket server uchun minimal logging"""
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    
    logger = logging.getLogger()
    logger.setLevel(logging.WARNING)  # Faqat WARNING va ERROR
    logger.handlers.clear()
    
    # Rotating file handler - 5MB max, 3 ta backup
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, 'socket_server.log'),
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Console - faqat ERROR
    console = logging.StreamHandler()
    console.setLevel(logging.ERROR)
    console.setFormatter(formatter)
    logger.addHandler(console)
    
    return logger


def setup_monitoring_logging():
    """Monitoring uchun detailed logging"""
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    
    # Rotating file handler - 20MB max, 10 ta backup
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, 'monitoring.log'),
        maxBytes=20 * 1024 * 1024,
        backupCount=10,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Console - INFO va yuqori
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(formatter)
    logger.addHandler(console)
    
    return logger