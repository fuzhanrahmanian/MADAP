import os
from madap.logger import logger
import pandas as pd
import numpy as np

log = logger.get_logger("data_acquisition")
EXTENSIONS = [".txt", ".csv", ".json", ".xlsx", ".hdf5", ".h5", ".pkl"]

def acquire_data(data_path):
    """Acquire data from a given file

    Args:
        data_path (str): The path to the data

    Returns:
       Pandas DataFrame: Dataframe with extracted data
    """
    _ , extension = os.path.splitext(data_path)

    log.info(f"Importing {extension} file.")

    if extension not in EXTENSIONS:
        log.error(f"Datatype not supported. Supported datatypes are: {EXTENSIONS}")
        raise ValueError("Datatype not supported")

    elif extension == ".csv" or extension ==".txt":
        df = pd.read_csv(data_path, sep=None, engine="python")
    elif extension == ".xlsx":
        df = pd.read_excel(data_path)
    elif extension == ".json":
        df = pd.read_json(data_path)
    elif extension == ".hdf5" or extension == ".h5":
        df = pd.read_hdf(data_path)
    elif extension == ".pkl":
        df = pd.read_pickle(data_path)

    return df


def format_data(data):
    """Convert the given data to the array of float

    Args:
        data (_type_): Given data

    Returns:
        A readable format of data for analysis
    """
    if not data is None:
        if not np.array_equal(data, data.astype(float)):
            data = data.astype(np.float)

    return data


def select_data(data, select_data:str):
    # this can be use when the user wants to select a subset of the data
    numbers = list(map(int, select_data.split(",")))
    data = data.iloc[numbers[0]:numbers[1], numbers[2]:numbers[3]].values.reshape(-1)
    return data

def choose_options(data):
    data_index = input("Choose 1 if you are selecting the header of your column, 2 if you are selecting the index of the rows/columns and 3 if is not available. \n Your selection is: ")
    if data_index == '1':
        ind = input(f"Name of the column of your choice (e.g. freq): ")
        data = data[ind]
    elif data_index == '2':
        ind = input(f"Number of rows and columns you are selecting (start_row,end_row,start_column,end_column  e.g. 1,10,2,3): ")
        data = select_data(data, ind)
    else:
        data = None
    return data


def format_plots(plots):
    if isinstance(plots, str):
        plots = [plots]
    if isinstance(plots, tuple):
        plots = list(plots)
    return plots

