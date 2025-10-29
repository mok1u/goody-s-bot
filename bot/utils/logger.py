import logging
import os
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime
import pytz

class MoscowTimeFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None):
        super().__init__(fmt, datefmt)
        self.moscow_tz = pytz.timezone('Europe/Moscow')
    
    def converter(self, timestamp):
        utc_dt = datetime.utcfromtimestamp(timestamp).replace(tzinfo=pytz.utc)
        moscow_dt = utc_dt.astimezone(self.moscow_tz)
        return moscow_dt
    
    def formatTime(self, record, datefmt=None):
        dt = self.converter(record.created)
        if datefmt:
            return dt.strftime(datefmt)
        else:
            return dt.strftime("%d.%m.%Y %H:%M:%S")

def setup_logger():
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    logger = logging.getLogger("vk_bot")
    logger.setLevel(logging.DEBUG)
    
    log_format = "%(asctime)s - %(levelname)s - %(message)s"
    formatter = MoscowTimeFormatter(log_format)
    
    log_file = os.path.join(log_dir, "log.log")
    
    file_handler = TimedRotatingFileHandler(
        filename=log_file,
        when="midnight",
        interval=1,
        backupCount=5,
        encoding="utf-8"
    )
    
    def namer(default_name):
        base_name = os.path.basename(default_name)
        if "." in base_name:
            date_part = base_name.split(".", 2)[-1]
            try:
                dt = datetime.strptime(date_part, "%Y-%m-%d")
                formatted_date = dt.strftime("%d.%m.%Y")
                return os.path.join(log_dir, f"{formatted_date}_log.log")
            except ValueError:
                return default_name
        return default_name
    
    file_handler.namer = namer
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)
    
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logger.propagate = False
    
    return logger

logger = setup_logger()

def log_debug(message, error=None):
    full_message = message
    if error:
        full_message += f" - {str(error)}"
    logger.debug(full_message)

def log_info(message, error=None):
    full_message = message
    if error:
        full_message += f" - {str(error)}"
    logger.info(full_message)

def log_warning(message, error=None):
    full_message = message
    if error:
        full_message += f" - {str(error)}"
    logger.warning(full_message)

def log_error(message, error=None):
    full_message = message
    if error:
        full_message += f" - {str(error)}"
    logger.error(full_message)

def log_critical(message, error=None):
    full_message = message
    if error:
        full_message += f" - {str(error)}"
    logger.critical(full_message)