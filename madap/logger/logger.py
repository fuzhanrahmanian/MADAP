import logging
import os
import sys
APP_LOGGER_NAME = 'MADAP'


def setup_applevel_logger(logger_name = APP_LOGGER_NAME, file_name=None):

    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(u"%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    streamHandler = logging.StreamHandler(sys.stdout)
    streamHandler.setFormatter(formatter)
    logger.handlers.clear()
    logger.addHandler(streamHandler)
    if file_name:
        if not os.path.exists("logs"):
            os.makedirs("logs")
        fh = logging.FileHandler(f"./logs/{file_name}", encoding="utf-8")
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    return logger

def get_logger(module_name):
   return logging.getLogger(APP_LOGGER_NAME).getChild(module_name)