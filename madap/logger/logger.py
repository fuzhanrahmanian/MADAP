"""This module defines the logger for the MADAP application."""
import sys
import queue

import logging
from logging.handlers import QueueHandler

APP_LOGGER_NAME = 'MADAP'
log_queue = queue.Queue()  # Queue for log messages

class QueueLoggerHandler(QueueHandler):
    """Custom handler for logging messages to queue"""

def setup_applevel_logger(logger_name=APP_LOGGER_NAME, file_name=None):
    """Sets up the app level logger

    Args:
        logger_name (str, optional): Logger name. Defaults to APP_LOGGER_NAME.
        file_name (str, optional): file name. Defaults to None.

    Returns:
        logger.Logger: app level logger
    """

    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)  # Set the logging level

    # Create handlers
    stream_handler = logging.StreamHandler(sys.stdout)
    queue_handler = QueueLoggerHandler(log_queue)  # Custom handler for queue

    # Create formatters and add it to handlers
    stream_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
    stream_handler.setFormatter(stream_format)

    # Add handlers to the logger
    logger.addHandler(stream_handler)
    logger.addHandler(queue_handler)

    if file_name:
        file_handler = logging.FileHandler(file_name)
        file_handler.setFormatter(stream_format)
        logger.addHandler(file_handler)

    return logger

def get_logger(module_name):
    """Returns a logger with the name of the module calling this function

    Args:
        module_name (str): name of the module calling this function

    Returns:
        logging.Logger: logger with the name of the module calling this function
    """
    return logging.getLogger(APP_LOGGER_NAME).getChild(module_name)
