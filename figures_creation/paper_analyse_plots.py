from math import exp
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
# activation_energy_calculated [mJ/mol]
# activation_energy_default [mJ/mol]
plotting.Plots()
expriment_type = "arrhenius" #["imp", "arrhenius"]
analysis_type = "calculated" #["calculated,", "default", "custom"]

save_dir = os.path.join(os.getcwd(), fr"electrolyte_figures/{expriment_type}_{analysis_type}")

data = pd.read_csv(os.path.join(os.getcwd(),r"data/Dataframe_STRUCTURED_all508.csv"), sep=";")
del data['Unnamed: 0']
MAPPED = True

# madap_resistance_default [Ohm]madap_resistance_default [Ohm]
# resistance [Ohm]

# madap_conductivity_default [S/cm]
# conductivity [S/cm]
def map_tamperature_values(data):
    equiv = {-30.0: 2, -20.0: 4, -10.0:6, 0.0:8, 10.0:10, 20.0:12, 30.0:14, 40.0:16, 50.0:18, 60.0:20}
    data["mapped_temp"] = data["temperature [°C]"].map(equiv)
    data.to_csv(os.path.join(os.getcwd(),r"data/Dataframe_STRUCTURED_all508.csv"), sep=";", index=True)

def calc_ratio_between_electrolyte_elements(data, CONCAT=False):
    Ec_PC_ratio = data["EC [g]"]/data["PC [g]"]
    EC_PC_EMC_ratio = round((data["EC [g]"] + data["PC [g]"])/ data["EMC [g]"], 1)


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
        data = pd.concat([data, pd.DataFrame(data["EC [g]"]/data["PC [g]"], columns= ["EC/PC [gr/gr]"])], axis= 1)
        data = pd.concat([data, pd.DataFrame(marker_sign, columns= ["marker"]) ], axis= 1)
        data.to_csv(os.path.join(os.getcwd(),r"data/Dataframe_STRUCTURED_all508.csv"), sep=";", index=True)
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

def text_legend(fig, ax, x0, y0, text, direction = "v", padpoints = 3, margin=1.,**kwargs):
    ha = kwargs.pop("ha", "right")
    va = kwargs.pop("va", "top")
    t = ax.figure.text(x0, y0, text, ha=ha, va=va, **kwargs)
    otrans = ax.figure.transFigure

    plt.tight_layout(pad=0)
    ax.figure.canvas.draw()
    plt.tight_layout(pad=0)
    offs =  t._bbox_patch.get_boxstyle().pad * t.get_size() + margin # adding 1pt
    trans = otrans + \
            matplotlib.transforms.ScaledTranslation(-offs/72.,-offs/72.,fig.dpi_scale_trans)
    t.set_transform(trans)
    ax.figure.canvas.draw()

    ppar = [0,-padpoints/72.] if direction == "v" else [-padpoints/72.,0]
    trans2 = matplotlib.transforms.ScaledTranslation(ppar[0],ppar[1],fig.dpi_scale_trans) + \
             ax.figure.transFigure.inverted()
    tbox = trans2.transform(t._bbox_patch.get_window_extent())
    bbox = ax.get_position()
    if direction=="v":
        ax.set_position([bbox.x0, bbox.y0,bbox.width, tbox[0][1]-bbox.y0])
    else:
        ax.set_position([bbox.x0, bbox.y0,tbox[0][0]-bbox.x0, bbox.height])


def analysis_plot_creation(data, EC_PC_EMC_ratio, save_dir, y_analysis = data["activation_energy_calculated [mJ/mol]"],
                            y_label = r"$E$ $[mJ/mol]$", fig_size = (4.9, 4), plot_name = "activation_EC_PC_EMC.svg", experiment_type = "impedance"):
    # plot the activation vs. (EC/PC) colorbar (LiPF6) scatter point circle and triangle for different EMC concentrationS
    fig, ax = plt.subplots(figsize=fig_size)
    if experiment_type == "arrhenius":
        scatter = mscatter(x=np.array(data["EC/PC [gr/gr]"]) , y=  np.array(y_analysis),\
                            c= np.array(data["LiPF6 [g]"]), s=9, m=data["marker"], ax=ax)
    if experiment_type == "impedance":
        scatter = mscatter(x=np.array(data["EC/PC [gr/gr]"]) , y=  np.array(y_analysis),\
                            c= np.array(data["LiPF6 [g]"]), s=np.array(data["mapped_temp"]), m=data["marker"], ax=ax)

    # Create a customize legend for the plot
    legend_elements = [Line2D([0], [0], marker='o', color='k', label=f"{EC_PC_EMC_ratio.unique()[0]}",
                            markerfacecolor='k', linestyle="None"),
                    Line2D([0], [0], marker='^', color='k', label=f"{EC_PC_EMC_ratio.unique()[1]}",
                            markerfacecolor='k', linestyle="None"),
                    Line2D([0], [0], marker='D', color='k', label=f'{EC_PC_EMC_ratio.unique()[2]}',
                            markerfacecolor='k', linestyle="None")] # , markersize=15

    # add colorbar
    cb = plt.colorbar(scatter)
    cb.set_label(label = r"$LiPF_6$ $[g]$")

    # add label to the axes
    plt.xlabel(r"$EC/PC$ $[gr/gr]$")
    plt.ylabel(y_label)

    # add legend to the plot according to the different EMC concentrations
    legend1= ax.legend(handles=legend_elements, prop={"size":6}, title= "(EC + PC): EMC", bbox_to_anchor=(1.50, 0.98), frameon= True)#, loc="best", frameon=False)
    ax.add_artist(legend1)

    # add second legend according to diffent temperature
    if experiment_type == "impedance":
        handles, lables = scatter.legend_elements(prop= "sizes") #, alpha = 0.6
        for i, val in enumerate(np.arange(-30, 70, 10)):
            lables[i] = fr"${float(val)}$"
        legend2 = ax.legend(handles=handles, labels=lables, title= "T [°C]", prop={"size":6}, bbox_to_anchor=(1.45, 0.7), frameon= True)



    #plt.show()
    plt.savefig(os.path.join(save_dir, plot_name))

if MAPPED:
    map_tamperature_values(data)
Ec_PC_ratio, EC_PC_EMC_ratio, marker_sign, data = calc_ratio_between_electrolyte_elements(data, CONCAT=False)
if expriment_type == "arrhenius":
    analysis_plot_creation(data, EC_PC_EMC_ratio, save_dir, y_analysis= data[f"activation_energy_{analysis_type} [mJ/mol]"], y_label = r"$E$ $[mJ/mol]$", fig_size = (5.7, 4.8), plot_name = f"arr_{analysis_type}.svg", experiment_type= expriment_type)
if expriment_type == "impedance":
    analysis_plot_creation(data, EC_PC_EMC_ratio, save_dir, y_analysis= data["madap_conductivity_default [S/cm]"], y_label = r"$\sigma$ $[S/cm]$", fig_size = (5.7, 4.8), plot_name = f"imp_{analysis_type}.svg", experiment_type = expriment_type)