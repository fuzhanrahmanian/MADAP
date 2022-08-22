import sys


import sys
import time
import json
import os

import pandas as pd

from madap.logger import logger



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
    dFrame = pd.DataFrame.from_dict(kwargs, orient = "index")
    dFrame = dFrame.transpose()
    return dFrame

def save_data_as_csv(directory, data, name):
    log.info(f"Saving data in {directory} as csv")
    data.to_csv(os.path.join(directory, name))


def save_data_as_json(directory, data, name):
    log.info(f"Saving data in {directory} as json")
    with open(os.path.join(directory, name), 'w', encoding="utf8") as f:
            json.dump(data, f, ensure_ascii=False)

def load_data_as_json(directory, name):
    with open(os.path.join(directory, name), 'r') as file:
            data = json.load(file)
    return data

def append_to_save_data(directory, added_data, name):
    data = load_data_as_json(directory, name)
    data.update(added_data)
    save_data_as_json(directory, data, name)