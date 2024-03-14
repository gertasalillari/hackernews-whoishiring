# logger_config.py
import os

from loguru import logger

LOGS_DIR = os.getenv("LOGS_DIR")
log_format = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {file}:{line} | {message}"

# Create the directory if it doesn't exist
os.makedirs(LOGS_DIR, exist_ok=True)

# Uncomment for removing logs printed to console (only to log file)
# logger.remove()

log_file_path = os.path.join(LOGS_DIR, "hn_post.log")
logger.add(log_file_path, format=log_format, rotation="30 day", level="INFO")
