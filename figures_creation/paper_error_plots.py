import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
import pandas as pd
import numpy as np

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.markers as mmarkers
from matplotlib.lines import Line2D

import matplotlib.gridspec as gridspec
from sklearn.preprocessing import QuantileTransformer, RobustScaler

#matplotlib.use('Agg')
matplotlib.rcParams["figure.max_open_warning"] = 1500

from madap.plotting import plotting

# activation_energy_calculated [mJ/mol]
# activation_energy_default [mJ/mol]
plotting.Plots()
expriment_type = "arrhenius" #["imp", "arrhenius"]
analysis_type = "calculated" #["calculated,", "default", "custom"]

save_dir = os.path.join(os.getcwd(), fr"electrolyte_figures") # {expriment_type}_{analysis_type}"

data = pd.read_csv(os.path.join(os.getcwd(),r"data/Dataframe_STRUCTURED_all508.csv"), sep=";")
del data['Unnamed: 0']

rmse_data = QuantileTransformer(output_distribution="normal").fit_transform(np.array(data["madap_rmse_default"]).reshape(-1, 1))
#rmse_data = data["madap_rmse_default"]
fig = plt.figure(figsize=(8,8))
gs = gridspec.GridSpec(3, 3)

ax_main = plt.subplot(gs[1:3, :2])
ax_xDist = plt.subplot(gs[0, :2],sharex=ax_main)
ax_yDist = plt.subplot(gs[1:3, 2],sharey=ax_main)

ax_main.scatter(np.array(data["conductivity [S/cm]"]), rmse_data, marker='.')
ax_main.set(xlabel="conductivity", ylabel="RMSE")

ax_xDist.hist(np.array(data["conductivity [S/cm]"]),bins=100,align='mid')
ax_xDist.set(ylabel='count')
ax_xCumDist = ax_xDist.twinx()
ax_xCumDist.hist(np.array(data["conductivity [S/cm]"]),bins=100,cumulative=True,histtype='step',density=True,color='r',align='mid')
ax_xCumDist.tick_params('y', colors='r')
ax_xCumDist.set_ylabel('cumulative',color='r')

ax_yDist.hist(rmse_data,bins=100,orientation='horizontal',align='mid')
ax_yDist.set(xlabel='count')

ax_yCumDist = ax_yDist.twiny()
ax_yCumDist.hist(rmse_data,bins=100,cumulative=True,histtype='step',density=True,color='r',align='mid',orientation='horizontal')
ax_yCumDist.tick_params('x', colors='r')
ax_yCumDist.set_xlabel('cumulative',color='r')

plt.savefig(os.path.join(save_dir, "test_hist.svg"))
