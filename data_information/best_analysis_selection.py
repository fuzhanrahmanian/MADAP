from ast import Pass
import os
import pandas as pd


# find the best analysis according to the nearest conductivity value
data_resistance = pd.read_csv(os.path.join(os.getcwd(),fr"data/comparison_data/resistance.csv"), sep=";")

del data_resistance["Unnamed: 0"]
del data_resistance["default_type1"]
del data_resistance["default_type3"]
del data_resistance["customtype1"]

#best_analysis_with_conductivtiy = []
best_analysis_with_resistance = []

for i in range(len(data_resistance)):
    selected_row_with_resistance = data_resistance.iloc[i].tolist()
    min_difference_with_nova_with_resistance = min(selected_row_with_resistance[2:-1], key=lambda x: abs(x - selected_row_with_resistance[-1]))
    best_analysis_with_resistance.append(data_resistance.columns[data_resistance.iloc[i].isin([min_difference_with_nova_with_resistance])][0])

data_resistance["best_analysis"] = best_analysis_with_resistance
# {'default_type4_random': 1068, 'default_type2': 1858, 'customtype1': 2150}

data_resistance.to_csv(os.path.join(os.getcwd(),r"data/comparison_data/resistance_best_analysis_default.csv"), sep=";")


