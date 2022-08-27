import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
import pandas as pd
import numpy as np

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.markers as mmarkers
from matplotlib.lines import Line2D



from madap.echem.e_impedance import e_impedance_plotting
eplot = e_impedance_plotting.ImpedancePlotting()

from madap.echem.arrhenius import arrhenius_plotting
aplot = arrhenius_plotting.ArrheniusPlotting()
# 'madap_rmse_default'
# 'activation_mse_calculated'
# 'activation_mse_default'


num_random_data = 4


experiment_type = "arrhenius" #["impedance", "arrhenius"]
analysis_type = "default" #["calculated,", "default", "custom"]


if experiment_type == "arrhenius":
    #error_type = f"activation_mse_{analysis_type}"
    log_conductivity, inverted_scale_temperatures = f"log_conductivity_{analysis_type}", f"inverted_scale_temperature_{analysis_type} [1000/K]"
    ln_conductivity_fit, activation = f"fitted_conductivity_{analysis_type} [S/cm]", f"activation_energy_{analysis_type} [mJ/mol]"
    arrhenius_constant, r2_score = f"activation_constant_{analysis_type} [S/cm]", f"activation_r2_score_{analysis_type}"
elif experiment_type == "impedance":
    chi, fit_data, custom_cicuit = 'madap_chi_square_default', 'predicted_impedance_default [Ohm]', "R0-p(R1,CPE1)"


save_dir = os.path.join(os.getcwd(), fr"electrolyte_figures") # {expriment_type}_{analysis_type}"

data = pd.read_csv(os.path.join(os.getcwd(),r"data/Dataframe_STRUCTURED_all508.csv"), sep=";")
del data['Unnamed: 0']

CREATE_QUANTILE = True
# function that return the quartile of madap_rmse_default
def find_quartile_label(data, quantile_column, column_name = "quantile_sign", CONCAT=False):
    quantile_value = data.sort_values(by = quantile_column, ascending=True)[quantile_column].quantile([0.25, 0.5, 0.75]).values
    #quantile_value = data[quantile_column].quantile([0.25, 0.5, 0.75]).values

    count_q1 = 0
    count_q2 = 0
    count_q3 = 0
    quantile_sign = []
    for i in range(len(data)):
        if data.loc[i, quantile_column] < quantile_value[0]:
            quantile_sign.append("Q1")
            count_q1 += 1
        elif data.loc[i, quantile_column] > quantile_value[2]:
            quantile_sign.append("Q3")
            count_q3 += 1
        else:
            quantile_sign.append("Q2")
            count_q2 += 1
    print(f"Q1: {count_q1} Q2: {count_q2} Q3: {count_q3}")
    if CONCAT:
        data = pd.concat([data, pd.DataFrame(quantile_sign, columns=[column_name]) ], axis= 1)
        data.to_csv(os.path.join(os.getcwd(),r"data/Dataframe_STRUCTURED_all508.csv"), sep=";", index=True)
    return data



def random_selection(data, column_name = "quantile_sign", num_random_data = 4, condition= "Q1", random_state = 42):
    selected_data = data.loc[data[column_name]== condition].sample(n=num_random_data, random_state = random_state)
    # need to return list of indeces
    return selected_data.index.values

if CREATE_QUANTILE:

    data = find_quartile_label(data, quantile_column = r2_score, column_name = f"quantile_sign_{r2_score}", CONCAT=False)



fig, ax = plt.subplots(3, num_random_data, figsize=(7, 7), sharex=True, sharey=True)
for i, quantile in enumerate(["Q1", "Q2", "Q3"]):
    random_indices = random_selection(data, column_name = f"quantile_sign_{r2_score}", num_random_data = num_random_data, condition= quantile)
    for j, num_random in enumerate(random_indices):
        if experiment_type == "impedance":
            # the required columns are:

            eplot.nyquist_fit(subplot_ax = ax[i, j],
                                frequency = eval(data["frequency [Hz]"][num_random]),
                                real_impedance = eval(data["real impedance Z' [Ohm]"][num_random]),
                                imaginary_impedance = eval(data["imaginary impedance Z' [Ohm]"][num_random]),
                                fitted_impedance= eval(data[fit_data][num_random]),
                                chi = data[chi][num_random],
                                suggested_circuit = custom_cicuit,
                                colorbar= False,
                                ax_sci_notation="both", scientific_limit=3,  scientific_label_colorbar=False,
                                legend_label=True, norm_color=True)

        if experiment_type == "arrhenius":
            exp_id = data["experimentID"][num_random]
            aplot.arrhenius_fit(subplot_ax = ax[i, j], temperatures = data["temperature [°C]"][data["experimentID"] == exp_id],
                                log_conductivity = data[log_conductivity][data["experimentID"] == exp_id],
                                inverted_scale_temperatures= data[inverted_scale_temperatures][data["experimentID"] == exp_id],
                                ln_conductivity_fit = data[ln_conductivity_fit][data["experimentID"] == exp_id],
                                activation = data[activation][data["experimentID"] == exp_id].values[0],
                                arrhenius_constant = data[arrhenius_constant][data["experimentID"] == exp_id].values[0],
                                r2_score = data[r2_score][data["experimentID"] == exp_id].values[0])#

            #aplot.ax1.axis("off")
            #aplot.ax1.get_legend().remove()
            aplot.ax1.set(xlabel="", ylabel="")
            aplot.ax2.set(xlabel="", ylabel="")
            # aplot.ax2.axes.get_yaxis().set_visible(False)
            # aplot.ax2.axes.get_xaxis().set_visible(False)
            # aplot.ax2.axes.get_yaxis().set_ticks([])
            # aplot.ax2.axes.get_xaxis().set_ticks([])
            aplot.ax2.axes.get_yticklabels()[0].set_visible(False)
            aplot.ax2.axes.get_xticklabels()[0].set_visible(False)

fig.tight_layout()
fig.text(-0.02, 0.85, 'Q1', va='center', rotation='vertical')
fig.text(-0.02, 0.5, 'Q2', va='center', rotation='vertical')
fig.text(-0.02, 0.15, 'Q3', va='center', rotation='vertical')
fig.text(0.5, -0.02, r"$\frac{1000}{T}$ $[K^{-1}]$", ha='center')
plt.savefig(os.path.join(os.getcwd(), fr"electrolyte_figures/error_{analysis_type}.svg"))

