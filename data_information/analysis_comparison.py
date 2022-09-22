from doctest import ELLIPSIS_MARKER
import os
import pandas as pd

RESISTANCE = True
CONDUCTIVITY = False

# type of analysis that have been done
analysis_type = ["default_type1", "default_type2", "default_type3", "customtype1", "default_type4_random", "default_christian"]
# resistance [Ohm];conductivity [S/cm]
# open an empty dataframe
result_resistance = pd.DataFrame()
result_conductivity = pd.DataFrame()

extracted_conductivity = []
extracted_resistance = []

for analysis in analysis_type:
    processed_data = pd.read_csv(os.path.join(os.getcwd(),fr"data/arr_data/processed_data_arr_and_impedance_{analysis}.csv"), sep=";")
    if analysis != "default_christian":
        extracted_conductivity.append(processed_data[f"madap_eis_conductivity_{analysis} [S/cm]"])
        extracted_resistance.append(processed_data[f"madap_eis_resistance_{analysis} [Ohm]"])
    else:
        extracted_conductivity.append(processed_data["conductivity [S/cm]"])
        extracted_resistance.append(processed_data["resistance [Ohm]"])

extracted_conductivity.insert(0 , processed_data["experimentID"])
extracted_resistance.insert(0, processed_data["experimentID"])

extracted_conductivity.insert(1, processed_data["temperature [°C]"])
extracted_resistance.insert(1, processed_data["temperature [°C]"])

result_conductivity = pd.concat(extracted_conductivity, axis=1)
result_resistance = pd.concat(extracted_resistance, axis=1)

analysis_type.insert(0, "experimentID")
analysis_type.insert(1, "temperature [°C]")

result_conductivity.columns, result_resistance.columns = analysis_type, analysis_type

# save the comparison data
result_conductivity.to_csv(os.path.join(os.getcwd(),fr"data/comparison_data/conductivity.csv"), sep=";")
result_resistance.to_csv(os.path.join(os.getcwd(),fr"data/comparison_data/resistance.csv"), sep=";")