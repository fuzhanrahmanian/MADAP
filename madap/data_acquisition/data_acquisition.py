import os
from madap import logger
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

    if not np.array_equal(data, data.astype(float)):
        data = data.astype(np.float)

    return data

def calculate_phaseshift(imaginary_impedance, real_impedance):
    """calculate phase shift

    Args:
        imaginary_impedance (class): imaginary impedance data
        real_impedance (class): real impedance data

    Returns:
        phase shift: calculated phase shift based on real and imaginary data
    """
    phase_shift_in_rad = np.arctan(format_data(abs(-imaginary_impedance)/format_data(abs(real_impedance))))
    return np.rad2deg(phase_shift_in_rad)
