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
from madap.echem.e_impedance import e_impedance as imp
from madap.data_acquisition import data_acquisition as da

plotting.Plots()
save_dir = os.path.join(os.getcwd(), r"electrolyte_figures/impedance_default")

data = pd.read_csv(os.path.join(os.getcwd(),r"data/Dataframe_STRUCTURED_all508.csv"), sep=";")
del data['Unnamed: 0']

def calc_ratio_between_electrolyte_elements(data, CONCAT=False):
    Ec_PC_ratio = data["EC"]/data["PC"]
    EC_PC_EMC_ratio = round((data["EC"] + data["PC"])/ data["EMC"], 1)


    # specify the figure markers
    marker_sign = []
    for i in range(len(data)):
        if EC_PC_EMC_ratio.unique()[0] == EC_PC_EMC_ratio.iloc[i]:
            marker_sign.append("o")
        elif EC_PC_EMC_ratio.unique()[1] == EC_PC_EMC_ratio.iloc[i]:
            marker_sign.append("^")
        elif EC_PC_EMC_ratio.unique()[2] == EC_PC_EMC_ratio.iloc[i]:
            marker_sign.append("D")
    if CONCAT:
        # append the EC/PC ratio to the dataFrame
        data = pd.concat([data, pd.DataFrame(data["EC"]/data["PC"], columns= ["EC/PC"])], axis= 1)
        data = pd.concat([data, pd.DataFrame(marker_sign, columns= ["marker"]) ], axis= 1)

    return Ec_PC_ratio, EC_PC_EMC_ratio, marker_sign, data

# define a list acceptable markers for the plot
def mscatter(x,y,ax=None, m=None, **kw):
    if not ax: ax=plt.gca()
    sc = ax.scatter(x,y,**kw)
    if (m is not None) and (len(m)==len(x)):
        paths = []
        for marker in m:
            if isinstance(marker, mmarkers.MarkerStyle):
                marker_obj = marker
            else:
                marker_obj = mmarkers.MarkerStyle(marker)
            path = marker_obj.get_path().transformed(
                        marker_obj.get_transform())
            paths.append(path)
        sc.set_paths(paths)
    return sc


def analysis_plot_creation(data, EC_PC_EMC_ratio, save_dir, y_analysis= data["activation_[mJ/mol]"], y_label = r"$E$ $[mJ/mol]$", fig_size = (4.9, 4), plot_name = "activation_EC_PC_EMC.svg"):
    # plot the activation vs. (EC/PC) colorbar (LiPF6) scatter point circle and triangle for different EMC concentrationS
    fig, ax = plt.subplots(figsize=fig_size)
    scatter = mscatter(x=np.array(data["EC/PC"]) , y=  np.array(y_analysis),\
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
    plt.ylabel(y_label)

    #plt.legend(handles, labels)
    plt.legend(handles=legend_elements)#, loc="best", frameon=False)
    #plt.show()
    plt.savefig(os.path.join(save_dir, plot_name))


Ec_PC_ratio, EC_PC_EMC_ratio, marker_sign, data = calc_ratio_between_electrolyte_elements(data, CONCAT=False)