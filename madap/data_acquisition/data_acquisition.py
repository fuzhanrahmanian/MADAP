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
        if isinstance(data, list):
            data = np.array(data, dtype=np.float64)

        if not np.array_equal(data, data.astype(float)):
            data = data.astype(np.float)

    return data


def select_data(data, select_data:str):
    # this can be use when the user wants to select a subset of the data
    numbers = list(map(int, select_data.split(",")))
    data = data.iloc[:, numbers[2]: numbers[3]].values.reshape(-1)
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

def remove_outlier_specifying_quantile(df, columnns, low_quantile = 0.05, high_quantile = 0.95):
    """removing the outliers from the data by specifying the quantile

    Args:
        df (dataframe): original dataframe
        columnns (list): colummns for which the outliers are to be removed
        low_quantile (float): lower quantile
        high_quantile (float): upper quantile

    Returns:
        data: the cleaned dataframe
    """
    # select the columns that needs to be studied for outliers
    detect_search = df[columnns]
    # Check if the low_quantile and high_quantile are floats, if not convert them to float
    if not isinstance(low_quantile, float):
        low_quantile = float(low_quantile)
    if not isinstance(high_quantile, float):
        high_quantile = float(high_quantile)
    # get the lower quantile of the corresponding columns
    q_low = detect_search.quantile(low_quantile)
    # get the upper quantile of the corresponding columns
    q_high = detect_search.quantile(high_quantile)
    # detect the outliiers in the data and replace those values with nan
    detect_search = detect_search[(detect_search < q_high) & (detect_search > q_low)]
    # find the index of the outliers
    nan_indices = [*set(np.where(np.asanyarray(np.isnan(detect_search)))[0].tolist())]
    log.info(f"The outliers are remove from dataset {detect_search} \n and the indeces are {nan_indices}.")

    return detect_search, nan_indices

def remove_nan_rows(df, nan_indices):
    # check if the index of the outliers is present in the dataframe
    available_nan_indices = [i for i in nan_indices if i in df.index.values]
    # removing the rows with nan and reset their indeces
    df = df.drop(df.index[available_nan_indices]).reset_index()
    # delete the columns
    if "index" in df.columns:
        del df["index"]
    remove_unnamed_col(df)
    return df


def remove_unnamed_col(df):
    if "Unnamed: 0" in df.columns:
        del df["Unnamed: 0"]
