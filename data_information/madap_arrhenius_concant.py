import os
import pandas as pd

data = pd.read_csv(os.path.join(os.getcwd(), r"data/final_version.csv"), sep=";")

del data["Unnamed: 0"]
del data["madap_arr_activation_energy [mJ/mol]"]
del data["madap_arr_activation_constant"]
del data["madap_arr_activation_r2_score"]
del data["madap_arr_activation_mse"]
del data["madap_arr_fitted_log_conductivity [ln(S/cm)]"]

data.to_csv(os.path.join(os.getcwd(), r"data/final_version_1.csv"), sep=";")