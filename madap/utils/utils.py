import os
import logger
import pandas as pd
import time

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


def assemble_file_name(*args):
    """_summary_

    Returns:
        _type_: _description_
    """
    timestamp = time.strftime("%Y%m%d_%H%M%S_")
    return timestamp+"_".join(list(args))

def assemble_data_frame(**kwargs):
    """_summary_

    Returns:
        _type_: _description_
    """
    dFrame = pd.DataFrame(data=kwargs)
    return dFrame

def save_data(directory, data, name):
    log.info(f"Saving data in {directory}")
    data.to_csv(os.path.join(directory, name))