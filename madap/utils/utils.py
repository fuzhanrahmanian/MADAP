import os
import logger

log = logger.get_logger("utils")

def create_dir(directory):
    """Checks if a directory is present, if not creates one at the given location

    Args:
        directory (str): Location where the directory should be created
    """

    if not os.path.exists(directory):
        os.makedirs(directory)
        log.info(f"Created directory {directory}.")
    else:
        log.info(f"Directory {directory} already exists.")
    return directory