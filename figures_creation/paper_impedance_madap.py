# impedance plots
# for loop EIS make plot for all, get the cell constant for each
# from the jsons extract conductivity and and resistance
# copy the current dataFrame and add predicted conductivity and resistance
# headers are ;experimentID;electrolyteLabel;PC;EC;EMC;LiPF6;inverseTemperature;temperature;conductivity;resistance;Z';Z'';frequency;electrolyteAmount
# plot conductivity vs. (EC/PC) colorbar (LiPF6/EMC)
# add default and get circuits to the dataFrame
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


DEFAULTTRAIN = True
CUSTOMTRAIN = False

plotting.Plots()
save_dir = os.path.join(os.getcwd(), r"electrolyte_figures/impedance")

plot_type = ["nyquist" ,"nyquist_fit", "residual", "bode"]

# load the data
data = pd.read_csv(os.path.join(os.getcwd(),r"data/Dataframe_STRUCTURED_all508.csv"), sep=";")
del data['Unnamed: 0']

# one time train without a custom circuit and with the default circuit
if DEFAULTTRAIN:
    for exp_id in tqdm(data["experimentID"].unique()):
        for temp in data["temperature [°C]"].unique():
        # get the data for the current experiment
            freq_data =eval(data.loc[(data["experimentID"] == exp_id) & (data["temperature [°C]"] == temp), "frequency [Hz]"][0])
            real_data = eval(data.loc[(data["experimentID"] == exp_id) & (data["temperature [°C]"] == temp), "real impedance Z' [Ohm]"][0])
            imag_data = eval(data.loc[(data["experimentID"] == exp_id) & (data["temperature [°C]"] == temp), "imaginary impedance Z'' [Ohm]"][0])
            phase_shift_data = None
            cell_constant = eval(data.loc[(data["experimentID"] == exp_id) & (data["temperature [°C]"] == temp), "cell constant, standard deviation"][0])[0]
            # initialize the Impedance class
            Im = imp.EImpedance(da.format_data(freq_data), da.format_data(real_data), da.format_data(imag_data), phase_shift_data)

            # initialis the EIS procedure
            Eis  = imp.EIS(Im, voltage=None, suggested_circuit="R0-p(R1,CPE1)",
                                    initial_value=[800,1e+14,1e-9,0.8], cell_constant = cell_constant)
            # analyze the data
            Eis.perform_all_actions(save_dir, plots = da.format_plots(plot_type), optional_name=exp_id)

            # add phaseshift, resistance, Conductivity , Circuit, circuits values, fit score RMSE, errors/confidance
            # "Fit": true, "Parameters": [1111.447578481177, 481035473447764.56, 7.910124148034937e-08, 0.881950020624159], 
            # "Confidence": [662.1935795742313, 0.007738940308997105, 9.150118977335364e-09, 0.015475407455327397], 
            # "rc_linKK": 6, "eval_fit_linKK": 0.7982701895051114, "RMSE_fit_error": 5154.242270867189,
            # "conductivity [S/cm]": 0.0018894278422646855}
            #1. phase_shift
            data.loc[(data["experimentID"] == exp_id) & (data["temperature [°C]"] == temp), "phase_shift \u03c6 [\u00b0]"] = Eis.impedance.phase_shift
            #2. conductivity
            data.loc[(data["experimentID"] == exp_id) & (data["temperature [°C]"] == temp), "madap_conductivity_default [S/cm]"] = Eis.conductivity
            #3. circuit that fit , type of fit, true or false
            #4. parameters plus theirs errors/confidance
            #5. RMSE of the fit
            #6. rc_linKK
            #7. eval_fit_linKK
            #8. resistance [Ohm]

if CUSTOMTRAIN: pass
# one time train with a custom circuit
        #print(data.head(n=20))

data.to_csv(os.path.join(os.getcwd(),r"data/CompleteDataWithimp.csv"), sep=";", index=True)
