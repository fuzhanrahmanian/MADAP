from cgitb import reset
import pandas as pd

RESISTANCE = True
CONDUCTIVITY = False

# type of analysis that have been done
analysis_type = ["default_type1", "default_type2", "default_type3", "customtype1", "default_type4_random", "default_christian"]

# open an empty dataframe
result = pd.DataFrame()

if RESISTANCE:
    pass

if CONDUCTIVITY:
    for analysis in analysis_type:
        processed_data = pd.read_csv(os.path.join(os.getcwd(),fr"data/arr_data/processed_data_arr_and_impedance_{analysis}.csv"), sep=";")
        result
