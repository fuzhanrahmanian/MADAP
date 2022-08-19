
#page 59 of nova spectroscopy:
#Rs (ohm): simululate the value of uncompensated resistance
#Rp (ohm): simulate polarization resistance (charge transfer resisitance)
#second one is constant
import matplotlib.colors as colors
import json
import matplotlib.pyplot as plt
import numpy as np
# from PyEIS import *
import json
import pandas as pd
# from scipy.signal import argrelextrema
# from sympy import symbols, Eq, solve
# from tqdm import tqdm
import pandas as pd
import matplotlib as mpl
import matplotlib
import matplotlib.legend_handler
mpl.rcParams.update(mpl.rcParamsDefault)
matplotlib.rc('font', size=20)
matplotlib.rc('axes', titlesize=20)
plt.style.use(['nature', 'science', 'no-latex'])
plt.rcParams['text.usetex'] = False
plt.rcParams['xtick.direction'] = 'in'
plt.rcParams['ytick.direction'] = 'in'
from matplotlib.lines import Line2D
eis_data = pd.read_csv(r"C:\Repositories\MADAP\for_test_8.csv")


fig, ax1 = plt.subplots(1, 1, figsize=(3, 3), constrained_layout=True)  # gridspec_kw={'hspace': 0.0} 'width_ratios': [1, 1]
cmap = "viridis"
#Z_norm = [eis_data['freq'][i] / (max(eis_data['freq']) - min(eis_data['freq'])) for i in range(len(eis_data['freq']))]
im = ax1.scatter(eis_data['real'], -eis_data['imag'], c=eis_data["freq"], #c=Z_norm,
                        cmap=None, #norm=colors.LogNorm(vmin=min(Z_norm), vmax=max(Z_norm)),
                        rasterized=True,label="V=20 [v]")
ax1.set_xlim([0, max(eis_data['real'])+200])
ax1.set_xticks(np.arange(0, max(eis_data['real']), max(eis_data['real'])/5), rotation=90, ha="right")
ax1.set_ylim([0.0, max(-eis_data['imag'])+200])
ax1.set_yticks(np.arange(0, max(-eis_data['imag']), max(-eis_data['imag'])/5))
# leg = ax1.legend(loc="upper left")
# leg.legendHandles[0].set_hatch(".")
# leg.legendHandles[0].set_color('k')
# leg.legendHandles[0].set_facecolors("k")
# leg.legendHandles[0].set_edgecolors("k")
handles, labels = ax1.get_legend_handles_labels()
new_handles= [Line2D([0], [0], marker='o', markerfacecolor="black", markeredgecolor="black", markersize=3, ls='')]
ax1.legend(new_handles, labels, loc="upper left")
ax1.set_xlabel(r"Z' $[\Omega]$", fontsize =12)
ax1.set_ylabel(r"-Z'' $[\Omega]$", fontsize =12)
ax1.xaxis.set_tick_params(rotation=0)
cb = plt.colorbar(im, ax=ax1)
cb.formatter.set_powerlimits((3, 3))
cb.update_ticks()
plt.show()