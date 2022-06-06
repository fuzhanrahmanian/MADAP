import os
from madap import logger
import pandas as pd

log = logger.get_logger("data_acquisition")
EXTENSIONS = [".txt", ".csv", ".json", ".xlsx", ".zip", ".hdf"]

def acquire_data(data_path):
    """Acquire data from a given file

    Args:
        data_path (str): The path to the data

    Returns:
       Pandas DataFrame: Dataframe with extracted data
    """
    _ , extension = os.path.splitext(data_path)

    if extension not in EXTENSIONS:
        log.error(f"Datatype not supported. Supported datatypes are: {EXTENSIONS}")
        raise ValueError("Datatype not supported")

    log.info(f"Importing {extension} file.")
    if extension == ".csv" or extension ==".txt":
        df = pd.read_csv(data_path, sep=None, engine="python")
    elif extension == ".xlsx":
        df = pd.read_excel(data_path)
    elif extension == ".json":
        df = pd.read_json(data_path)
    elif

    return df

