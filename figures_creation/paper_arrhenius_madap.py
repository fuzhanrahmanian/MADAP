# arrhenius plots
# for loop arrhenius make plot for all, get the activation and arrhenius constant for each
# group the data by experiment id and electrolyte label
# from the jsons extract activation and cell constant
# copy the current dataFrame and add predicted activation and cell constant
# headers are ;experimentID;electrolyteLabel;PC;EC;EMC;LiPF6;inverseTemperature;temperature;conductivity;resistance;Z';Z'';frequency;electrolyteAmount
# plot activation vs. (EC/PC) colorbar (LiPF6) scatter point circle and triangle for different EMC concentrationS
# add an activation parameter to the dataFrame
<<<<<<< HEAD
=======
from cmath import exp
>>>>>>> 4617e37 (added scripts for figure creation)
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
from tqdm import tqdm
import pandas as pd
<<<<<<< HEAD
import numpy as np
from tqdm import tqdm

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.markers as mmarkers
from matplotlib.lines import Line2D
#matplotlib.use('Agg')
=======
from fractions import Fraction

import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Agg')
>>>>>>> 4617e37 (added scripts for figure creation)
matplotlib.rcParams["figure.max_open_warning"] = 1500

from madap.plotting import plotting
from madap.echem.arrhenius import arrhenius as arr
from madap.data_acquisition import data_acquisition as da

<<<<<<< HEAD
plotting.Plots()
save_dir = os.path.join(os.getcwd(), r"electrolyte_figures/arrhenius")

plot_type = ["arrhenius", "arrhenius_fit"]

# load the data
data = pd.read_csv(os.path.join(os.getcwd(),r"data/Dataframe_STRUCTURED_all508.csv"), sep=";")
del data['Unnamed: 0']

for exp_id in tqdm(data["experimentID"].unique()):
    # get the data for the current experiment
    temp_exp = data["temperature [°C]"][data["experimentID"] == exp_id]
    cond_exp = data["conductivity [S/cm]"][data["experimentID"] == exp_id]

    # initialize the Arrhenius class
    Arr = arr.Arrhenius(da.format_data(temp_exp), da.format_data(cond_exp))
    # analyze the data
    Arr.perform_all_actions(save_dir, plots = da.format_plots(plot_type), optional_name=exp_id)

    # add fit score, activation constant and activation to the dataFrame
    data.loc[data["experimentID"] == exp_id, "activation_energy [mJ/mol]"] = Arr.activation
    data.loc[data["experimentID"] == exp_id, "activation_constant [S/cm]"] = Arr.arrhenius_constant
    data.loc[data["experimentID"] == exp_id, "activation_r2_score"] = Arr.fit_score
    data.loc[data["experimentID"] == exp_id, "activation_mse"] = Arr.mse_calc

    #print(data.head(n=20))
data.to_csv(os.path.join(os.getcwd(),r"data/Dataframe_STRUCTURED_all508_arr.csv"), sep=";", index=True)

data.to_csv(os.path.join(os.getcwd(),r"data/Dataframe_STRUCTURED_all508.csv"), sep=";", index=True, mode='w+')

=======
TRAIN = False
save_dir = os.path.join(os.getcwd(), r"electrolyte_figures/arrhenius")

# fit the data if TRAIN is True, otherwise plot the activation according to different PC, EC, EMC, LiPF6 parameters
if TRAIN:

    plot_type = ["arrhenius", "arrhenius_fit"]

    # load the data
    data = pd.read_csv(os.path.join(os.getcwd(),r"data/CompleteData.csv"), sep=";")
    del data['Unnamed: 0']

    for exp_id in tqdm(data["experimentID"].unique()):
        # get the data for the current experiment
        temp_exp = data["temperature"][data["experimentID"] == exp_id]
        cond_exp = data["conductivity"][data["experimentID"] == exp_id]

        # initialize the Arrhenius class
        Arr = arr.Arrhenius(da.format_data(temp_exp), da.format_data(cond_exp))
        # analyze the data
        Arr.perform_all_actions(save_dir, plots = da.format_plots(plot_type), optional_name=exp_id)

        # add fit score, activation constant and activation to the dataFrame
        data.loc[data["experimentID"] == exp_id, "activation_[mJ/mol]"] = Arr.activation
        data.loc[data["experimentID"] == exp_id, "activation_constant_[S/cm]"] = Arr.arrhenius_constant
        data.loc[data["experimentID"] == exp_id, "activation_fit_score"] = Arr.fit_score

        #print(data.head(n=20))

    data.to_csv(os.path.join(os.getcwd(),r"data/CompleteDataWithArr.csv"), sep=";", index=True)

# round((data["EC"] + data["PC"])/ data["EMC"], 1).unique()



data = pd.read_csv(os.path.join(os.getcwd(),r"data/CompleteDataWithArr.csv"), sep=";")
del data['Unnamed: 0']
# plot the predicted activation for each batch of the experiment
point_size = [5* (i+1) for i,_ in enumerate(data["temperature"].unique())]
markers = ["o", "^", "D"]
fraction_ratio = [Fraction(perc) for perc in round((data["EC"] + data["PC"])/ data["EMC"], 1).unique()]

sp = plt.scatter(data["EC"]/data["PC"], data["activation_[mJ/mol]"], \
            marker = round((data["EC"] + data["PC"])/ data["EMC"], 1),\
            c = data["LiPF6"], cmap = "viridis", s = point_size, ls = "none")
            #label = data["temperauter"], alpha = 0.5)

# manage multilegend
f = lambda m,s: plt.scatter([], [], marker = m, s = s, ls = "none")[0]

handles = [f("s", point_size[i]) for i in range(len(point_size))]
handles += [f(markers[i], "k") for i in range(len(markers))]

labels = point_size, [f"(EC + PC): EMC = {fraction_ratio[0]}",\
                        f"(EC + PC): EMC = {fraction_ratio[1]}",\
                        f"(EC + PC): EMC = {fraction_ratio[2]}"]

# add colorbar
cb = plt.colorbar(sp)
cb.set_label(label = r"LiPF_6 [gr]")

# add label to the axes
plt.xlabel("EC/PC [gr/gr")
plt.ylabel("E [mJ/mol]")

plt.legend(handles, labels)
plt.show()
#plt.savefig(os.path.join(save_dir, "activation_EC_PC_EMC.png"))
>>>>>>> 4617e37 (added scripts for figure creation)
