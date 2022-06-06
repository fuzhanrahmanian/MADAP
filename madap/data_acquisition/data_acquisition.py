import os
from madap import logger
import pandas as pd

log = logger.get_logger("data_acquisition")
EXTENSIONS = [".txt", ".csv"]

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


    if extension == ".csv" or extension ==".txt":
        log.info(f"Importing {extension} file.")
        df = pd.read_csv(data_path, sep=None, engine="python")

    

    return df

