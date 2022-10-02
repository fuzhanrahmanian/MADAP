"""This module is responsible for handaling the data acquisition and data cleaning into MADAP"""
import os
import pandas as pd
import numpy as np

from madap.logger import logger


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

    if extension in (".csv", ".txt"):
        try:
            df = pd.read_csv(data_path, sep=None, engine="python")
        except:
            df = pd.read_csv(data_path, sep=";", engine="python")

    if extension == ".xlsx":
        df = pd.read_excel(data_path)
    if extension == ".json":
        df = pd.read_json(data_path)
    if extension in (".hdf5", ".h5"):
        df = pd.read_hdf(data_path)
    if extension == ".pkl":
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


def select_data(data, selected_data:str):
    """ Function to subselect the data from the dataframe

    Args:
        data (DataFrame): The dataframe from which the data is to be selected
        select_data (str): The string containing the start and end row and column

    Returns:
        DataFrame: The subselected dataframe
    """
    numbers = list(map(int, selected_data.split(",")))
    data = data.iloc[:, numbers[2]: numbers[3]].values.reshape(-1)

    # check datatype
    if not isinstance(data, np.ndarray):
        data = np.array(data)
    if isinstance(data[0], str):
        if len(data) == 1:
            data = np.array(eval(data[0]))
        else:
            for i in range(len(data)):
                data[i] = eval(data[i])

    return data


def format_plots(plots):
    """ Format the selection plots into a list

    Args:
        plots (obj): The plots selected by the user

    Returns:
        list: The list of plots selected by the user
    """
    if isinstance(plots, str):
        plots = [plots]
    if isinstance(plots, tuple):
        plots = list(plots)
    return plots

def remove_outlier_specifying_quantile(df, columns, low_quantile = 0.05, high_quantile = 0.95):
    """removing the outliers from the data by specifying the quantile

    Args:
        df (dataframe): original dataframe
        columns (list): colummns for which the outliers are to be removed
        low_quantile (float): lower quantile
        high_quantile (float): upper quantile

    Returns:
        data: the cleaned dataframe
    """
    # select the columns that needs to be studied for outliers
    detect_search = df[columns]
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
    log.info(f"The outliers are remove from dataset {detect_search} \
               \n and the indeces are {nan_indices}.")

    return detect_search, nan_indices

def remove_nan_rows(df, nan_indices):
    """ Remove the rows with nan values

    Args:
        df (DataFramo): The dataframe from which the rows are to be removed
        nan_indices (list): The list of indices of the rows to be removed

    Returns:
        DataFrame: The dataframe with the rows removed
    """
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
    """ Remove the unnamed columns from the dataframe

    Args:
        df (DataFrame): The dataframe from which unnamed cloums were removed
    """
    if "Unnamed: 0" in df.columns:
        del df["Unnamed: 0"]
