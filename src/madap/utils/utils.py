""" This module defines some utility functions for the MADAP project. """
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
    """Assemble a file name from the given arguments

    Returns:
        str: The assembled file name
    """
    timestamp = time.strftime("%Y%m%d_%H%M%S_")
    return timestamp+"_".join(list(args))

def assemble_data_frame(**kwargs):
    """Assemble a data frame from the given arguments

    Returns:
        Pandas DataFrame: The assembled data frame
    """
    try:
        df = pd.DataFrame.from_dict(kwargs, orient = "index")
        df = df.transpose()
    except AttributeError:
        df = pd.DataFrame(data=kwargs)
    return df

def save_data_as_csv(directory, data, name):
    """Save the given data as csv

    Args:
        directory (str): The directory where the data should be saved
        data (Pandas DataFrame): The data that should be saved
        name (str): The name of the file
    """
    log.info(f"Saving data in {directory} as csv")
    data.to_csv(os.path.join(directory, name))


def save_data_as_json(directory, data, name):
    """Save the given data as json

    Args:
        directory (str): The directory where the data should be saved
        data (dict): The data that should be saved
        name (str): The name of the file
    """
    log.info(f"Saving data in {directory} as json")
    with open(os.path.join(directory, name), 'w') as file:
        json.dump(data, file)
    log.info(f"Saving data in {directory} as json")
    with open(os.path.join(directory, name), 'w', encoding="utf8") as f:
        json.dump(data, f, ensure_ascii=False)

def load_data_as_json(directory, name):
    """ Load the given data as json

    Args:
        directory (str): The directory where the data should be saved
        name (str): The name of the file
    """
    log.info(f"Loading data from {directory} as json")
    with open(os.path.join(directory, name), 'r') as file:
        data = json.load(file)
    return data

def append_to_save_data(directory, added_data, name):
    """Append the given data to the existing data

    Args:
        directory (str): The directory where the data should be saved
        added_data (Pandas DataFrame): The data that should be appended
        name (str): The name of the file
    """
    data = load_data_as_json(directory, name)
    data.update(added_data)
    save_data_as_json(directory, data, name)
