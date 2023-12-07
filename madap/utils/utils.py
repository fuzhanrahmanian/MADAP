""" This module defines some utility functions for the MADAP project. """
import time
import json
import os

import numpy as np
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
    log.info(f"Saving data in {directory}.csv")
    data.to_csv(os.path.join(directory, name))


def save_data_as_json(directory, data, name):
    """Save the given data as json

    Args:
        directory (str): The directory where the data should be saved
        data (dict): The data that should be saved
        name (str): The name of the file
    """
    log.info(f"Saving data in {directory}.json")
    with open(os.path.join(directory, name), 'w', encoding="utf-8") as file:
        json.dump(data, file)


def load_data_as_json(directory, name):
    """ Load the given data as json

    Args:
        directory (str): The directory where the data should be saved
        name (str): The name of the file
    """
    log.info(f"Loading data from {directory} as json")
    with open(os.path.join(directory, name), 'r', encoding="utf-8") as file:
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


def convert_numpy_to_python(data):
    """Convert numpy data to python data

    Args:
        data (pandas.DataFrame): The data that should be converted

    Returns:
        pd.DataFrame: The converted data
    """
    # serializing numpy data to python data
    if isinstance(data, dict):
        return {k: convert_numpy_to_python(v) for k, v in data.items()}
    # serializing numpy int to python int
    elif isinstance(data, (np.int64, np.int32, np.int16, np.int8)):
        return int(data)
    # serializing numpy float to python float
    elif isinstance(data, (np.float64, np.float32, np.float16)):
        return float(data)
    # serializing numpy array to python list
    elif isinstance(data, (np.ndarray,)):
        return data.tolist()

    return data
