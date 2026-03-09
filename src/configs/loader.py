import os
import json
import time
import logging

from logging.handlers import RotatingFileHandler

date_format = "%d-%m-%Y %H.%M.%S"

local_time = time.localtime()
time_format = time.strftime(date_format, local_time)

os.makedirs("logs", exist_ok=True)
os.makedirs("schedule", exist_ok=True)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

file_handler = RotatingFileHandler(
    filename=f"logs/log {time_format}.log",
    maxBytes=5242880,
    backupCount=5,
    encoding="UTF-8"
)

file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(
    logging.Formatter(
        "%(asctime)s %(levelname)s\t%(funcName)s %(message)s",
        datefmt=date_format
    )
)

logger.addHandler(file_handler)

stream_handler = logging.StreamHandler()

stream_handler.setLevel(logging.INFO)
stream_handler.setFormatter(
    logging.Formatter(
        "%(asctime)s %(levelname)s\t%(message)s", 
        datefmt="%d-%m-%Y %H:%M:%S"
    )
)

logger.addHandler(stream_handler)

def loadConfig() -> dict:
    with open("./config.json", "r", encoding="UTF-8") as f:
        config = json.load(f)

    logging.info("config.json loaded")

    return config