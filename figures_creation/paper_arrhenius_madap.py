# arrhenius plots
# for loop arrhenius make plot for all, get the activation and arrhenius constant for each
# group the data by experiment id and electrolyte label
# from the jsons extract activation and cell constant
# copy the current dataFrame and add predicted activation and cell constant
# headers are ;experimentID;electrolyteLabel;PC;EC;EMC;LiPF6;inverseTemperature;temperature;conductivity;resistance;Z';Z'';frequency;electrolyteAmount
# plot activation vs. (EC/PC) colorbar (LiPF6) scatter point circle and triangle for different EMC concentrationS
# add an activation parameter to the dataFrame
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
from tqdm import tqdm
import pandas as pd
import numpy as np

import matplotlib

#matplotlib.use('Agg')
matplotlib.rcParams["figure.max_open_warning"] = 1500

from madap.plotting import plotting
from madap.echem.arrhenius import arrhenius as arr
from madap.data_acquisition import data_acquisition as da

name = "madap"    #"default_christian" #["default_type1", "default_type2", "default_type3", "customtype1", "default_type4_random", default_christian]
# , "default_christian" should be try separately
#analysis_type = "default_with_initial_value" #["default", "custom", "default_with_initial_value", "calculated"]

from joblib import Parallel, delayed
from joblib import Memory
location = fr"figures_creation/cache_dir_arr_{name}"
memory = Memory(location, verbose=True)


plotting.Plots()
save_dir = os.path.join(os.getcwd(), fr"electrolyte_figures/arrhenius_{name}")

plot_type = ["arrhenius", "arrhenius_fit"]
#analysis_type = "default"  # ["calculated", "custom", "default"]
# load the data
if name == "default_christian":
    data = pd.read_csv(os.path.join(os.getcwd(),r"data/Dataframe_STRUCTURED_all508.csv"), sep=";")
if (name != "default_christian") and (name != "madap"):
    data = pd.read_csv(os.path.join(os.getcwd(),fr"data/processed_data_impedance_{name}.csv"), sep=";")
if name == "madap":
    data = pd.read_csv(os.path.join(os.getcwd(),fr"data/final_version_8.csv"), sep=";")
del data['Unnamed: 0']

## write an empty dataset and append the train stuff to the main after parallel training.

def concat_new_data(data, exp_id, Arr):#, analysis_type):
    # 1. activation
    data.loc[data["experimentID"] == exp_id, f"activation_energy [mJ/mol]"] = Arr.activation
    # 2. cell constant
    data.loc[data["experimentID"] == exp_id, f"activation_constant"] = Arr.arrhenius_constant
    # 3. r2 score
    data.loc[data["experimentID"] == exp_id, f"activation_r2_score"] = Arr.fit_score
    # 4. mse score
    data.loc[data["experimentID"] == exp_id, f"activation_mse"] = Arr.mse_calc
    # 5. log conductivity
    #data.loc[data["experimentID"] == exp_id, f"log_conductivity_{analysis_type}"] = Arr._log_conductivity()
    # 6. inverted scale temperature
    #data.loc[data["experimentID"] == exp_id, f"inverted_scale_temperature_{analysis_type} [1000/K]"] = Arr.inverted_scale_temperatures
    # 7 fitted conductivity
    data.loc[data["experimentID"] == exp_id, f"fitted_log_conductivity [ln(S/cm)]"] = Arr.ln_conductivity_fit


def constly_compute(data, exp_id, name):
    # get the data for the current experiment
    temp_exp = data["temperature [°C]"][data["experimentID"] == exp_id]
    if (name != "default_christian") and (name != "madap"):
        cond_exp = data[f"madap_eis_conductivity_{name} [S/cm]"][data["experimentID"] == exp_id]
    if name == "default_christian":
        cond_exp = data[f"conductivity [S/cm]"][data["experimentID"] == exp_id]
    if name == "madap":
        cond_exp = data[f"madap_eis_conductivity [S/cm]"][data["experimentID"] == exp_id]
    # initialize the Arrhenius class
    Arr = arr.Arrhenius(da.format_data(temp_exp), da.format_data(cond_exp))
    # analyze the data
    Arr.perform_all_actions(save_dir, plots = da.format_plots(plot_type), optional_name=exp_id)


    #data.to_csv(os.path.join(os.getcwd(), fr"data/Dataframe_STRUCTURED_all508_arr_{analysis_type}.csv"), sep=";", index=True)

constly_compute_cached = memory.cache(constly_compute)


def data_processing_using_cache(data, exp_id, analysis_type):
    return constly_compute_cached(data, exp_id, analysis_type)

Parallel(n_jobs=10)(delayed(data_processing_using_cache)(data, exp_id, name) for exp_id in tqdm(data["experimentID"].unique()))
# for exp_id in tqdm(data["experimentID"].unique()):w
#     constly_compute(data, exp_id, name)


# for exp_id in tqdm(data["experimentID"].unique()):
#data.to_csv(os.path.join(os.getcwd(),r"data/Dataframe_STRUCTURED_all508.csv"), sep=";", index=True, mode='w+')