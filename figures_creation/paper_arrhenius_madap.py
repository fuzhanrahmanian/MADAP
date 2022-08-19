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
from tqdm import tqdm

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.markers as mmarkers
from matplotlib.lines import Line2D
#matplotlib.use('Agg')
matplotlib.rcParams["figure.max_open_warning"] = 1500

from madap.plotting import plotting
from madap.echem.arrhenius import arrhenius as arr
from madap.data_acquisition import data_acquisition as da

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

# plot the activation vs. (EC/PC) colorbar (LiPF6) scatter point circle and triangle for different EMC concentrationS
fig, ax = plt.subplots(figsize=(4.9,4))
scatter = mscatter(x=np.array(data["EC/PC"]) , y=  np.array(data["activation_[mJ/mol]"]),\
                    c= np.array(data["LiPF6"]), s=9, m=data["marker"], ax=ax)

# Create a customize legend for the plot
legend_elements = [Line2D([0], [0], marker='o', color='k', label=f"(EC + PC): EMC = {EC_PC_EMC_ratio.unique()[0]}",
                          markerfacecolor='k', linestyle="None"),
                   Line2D([0], [0], marker='^', color='k', label=f"(EC + PC): EMC = {EC_PC_EMC_ratio.unique()[1]}",
                          markerfacecolor='k', linestyle="None"),
                   Line2D([0], [0], marker='D', color='k', label=f'(EC + PC): EMC = {EC_PC_EMC_ratio.unique()[2]}',
                          markerfacecolor='k', linestyle="None")] # , markersize=15

# add colorbar
cb = plt.colorbar(scatter)
cb.set_label(label = r"$LiPF_6$ $[g]$")

# add label to the axes
plt.xlabel(r"$EC/PC$ $[g/g]$")
plt.ylabel(r"$E$ $[mJ/mol]$")

#plt.legend(handles, labels)
plt.legend(handles=legend_elements)#, loc="best", frameon=False)

#plt.show()
plt.savefig(os.path.join(save_dir, "activation_EC_PC_EMC.svg"))
