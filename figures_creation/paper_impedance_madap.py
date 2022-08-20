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
import re
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
temperatures = data["temperature [°C]"].unique().tolist()
temperatures.sort()
# one time train without a custom circuit and with the default circuit
if DEFAULTTRAIN:
    suggested_circuit="R0-p(R1,CPE1)"
    initial_value=[800,1e+14,1e-9,0.8]
else:
    suggested_circuit= None
    initial_value= None

ind_data = 0
for exp_id in tqdm(data["experimentID"].unique()):
    for temp in tqdm(temperatures):
    # get the data for the current experiment
        print(f"The index is {ind_data}")
        print(len(data.loc[(data["experimentID"] == exp_id) & (data["temperature [°C]"] == temp), "frequency [Hz]"]))
        if len(data.loc[(data["experimentID"] == exp_id) & (data["temperature [°C]"] == temp), "frequency [Hz]"]) != 0:
            freq_data = eval(data.loc[(data["experimentID"] == exp_id) & (data["temperature [°C]"] == temp), "frequency [Hz]"][ind_data])
            real_data = eval(data.loc[(data["experimentID"] == exp_id) & (data["temperature [°C]"] == temp), "real impedance Z' [Ohm]"][ind_data])
            imag_data = eval(data.loc[(data["experimentID"] == exp_id) & (data["temperature [°C]"] == temp), "imaginary impedance Z'' [Ohm]"][ind_data])
            phase_shift_data = None
            cell_constant = float(re.findall(r'\b(\d*\.?\d+)', data.loc[(data["experimentID"] == exp_id) & (data["temperature [°C]"] == temp), "cell constant, standard deviation"][ind_data])[0])

            # initialize the Impedance class
            Im = imp.EImpedance(da.format_data(freq_data), da.format_data(real_data), da.format_data(imag_data), phase_shift_data)

            # initialis the EIS procedure
            Eis  = imp.EIS(Im, voltage=None, suggested_circuit=suggested_circuit,
                                    initial_value=initial_value, cell_constant = cell_constant)
            # analyze the data
            Eis.perform_all_actions(save_dir, plots = da.format_plots(plot_type), optional_name=exp_id)

            #1. phase_shift
            data.loc[(data["experimentID"] == exp_id) & (data["temperature [°C]"] == temp), "phase_shift \u03c6 [\u00b0]"] = str(Eis.impedance.phase_shift)
            #2. conductivity
            data.loc[(data["experimentID"] == exp_id) & (data["temperature [°C]"] == temp), "madap_conductivity_default [S/cm]"] = Eis.conductivity
            #3. parameters plus theirs errors/confidance
            data.loc[(data["experimentID"] == exp_id) & (data["temperature [°C]"] == temp), "madap_fit_params_default"] = str([(val, err) for val, err in zip(Eis.custom_circuit.parameters_, Eis.custom_circuit.conf_)])
            #4. RMSE of the fit
            data.loc[(data["experimentID"] == exp_id) & (data["temperature [°C]"] == temp), "madap_rmse_default"] = Eis.rmse_calc
            #5. num_rc_linKK
            data.loc[(data["experimentID"] == exp_id) & (data["temperature [°C]"] == temp), "madap_num_rc_linKK_default"] = Eis.num_rc_linkk
            #6. eval_fit_linKK
            data.loc[(data["experimentID"] == exp_id) & (data["temperature [°C]"] == temp), "madao_eval_fit_linKK_default"] = Eis.eval_fit_linkk
            #7. resistance [Ohm]
            data.loc[(data["experimentID"] == exp_id) & (data["temperature [°C]"] == temp), "madap_resistance_default [Ohm"]=  Eis.custom_circuit.parameters_[0]
            #8 chi_value
            data.loc[(data["experimentID"] == exp_id) & (data["temperature [°C]"] == temp), "madap_chi_square_dafault"] = Eis.chi_val
            ind_data += 1

data.to_csv(os.path.join(os.getcwd(),r"data/Dataframe_STRUCTURED_all508_imp.csv"), sep=";", index=True)

data.to_csv(os.path.join(os.getcwd(),r"data/Dataframe_STRUCTURED_all508.csv"), sep=";", index=True)