import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
import pandas as pd
import numpy as np


import matplotlib.pyplot as plt

from mpl_toolkits.axes_grid1 import make_axes_locatable



from madap.echem.e_impedance import e_impedance_plotting
eplot = e_impedance_plotting.ImpedancePlotting()

from madap.echem.arrhenius import arrhenius_plotting
aplot = arrhenius_plotting.ArrheniusPlotting()
# 'madap_rmse_default'
# 'activation_mse_calculated'
# 'activation_mse_default'

save_dir = os.path.join(os.getcwd(), fr"electrolyte_figures") # {expriment_type}_{analysis_type}"

data = pd.read_csv(os.path.join(os.getcwd(),r"data\final_version_10.csv"), sep=";")
del data['Unnamed: 0']

num_random_data = 4


experiment_type = "impedance" #["impedance", "arrhenius"]
# analysis_type = "default" #["calculated,", "default", "custom"]
def log_conductivity_calc(conductivity):
    """Convert the conductivity to log scale.

    Returns:
        np.array: Log of the conductivity.
    """
    return np.log(conductivity)

def cel_to_thousand_over_kelvin(temperatures):
    """Convert the temperatures from Celcius to 1000/K.
    """
    return 1000/(temperatures + 273.15)


if experiment_type == "arrhenius":
    #error_type = f"activation_mse_{analysis_type}"
    temperatures, conductivity = 'temperature [°C]', 'madap_eis_conductivity [S/cm]'
    log_conductivity, inverted_scale_temperatures = log_conductivity_calc(data[conductivity]), cel_to_thousand_over_kelvin(data[temperatures])
    # Create a dataframe with two columns l and it where the values are log_conductivity and inverted_scale_temperatures

    data["log_conductivity"] = pd.Series(log_conductivity)
    data["inverted_scale_temperatures"] = pd.Series(inverted_scale_temperatures)
    #data.to_csv(os.path.join(os.getcwd(),r"data\final_version_11.csv"), sep=";", index=True)

    ln_conductivity_fit, activation = "madap_arr_fitted_log_conductivity [ln(S/cm)]", "madap_arr_activation_energy [mJ/mol]"
    arrhenius_constant, r2_score = "madap_arr_activation_constant", "madap_arr_activation_r2_score"
elif experiment_type == "impedance":
    chi, fit_data, custom_cicuit = 'madap_eis_chi_square', 'madap_eis_predicted_impedance [Ohm]', "madap_eis_custom_circuit"
    r2_score = 'madap_eis_rmse'


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
        data.to_csv(os.path.join(os.getcwd(),r"data\final_version_11.csv"), sep=";", index=True)
    return data



def random_selection(data, column_name = "quantile_sign", num_random_data = 4, condition= "Q1", random_state = 7):
    selected_data = data.loc[data[column_name]== condition].sample(n=num_random_data, random_state = random_state)
    # need to return list of indeces
    return selected_data.index.values

if CREATE_QUANTILE:

    data = find_quartile_label(data, quantile_column = r2_score, column_name = f"quantile_sign_{r2_score}", CONCAT=True)

figsize = (9, 7)

fig, ax = plt.subplots(3, num_random_data, figsize=figsize, sharex=True, sharey=True)
for i, quantile in enumerate(["Q1", "Q2", "Q3"]):
    random_indices = random_selection(data, column_name = f"quantile_sign_{r2_score}", num_random_data = num_random_data, condition= quantile)
    for j, num_random in enumerate(random_indices):
        if experiment_type == "impedance":
            # the required columns are:
            # Make all subplot square
            data_len = len(eval(data[fit_data][num_random]))
            im = eplot.nyquist_fit(subplot_ax = ax[i, j],
                                frequency = eval(data["frequency [Hz]"][num_random])[:data_len+5],
                                real_impedance = np.array(eval(data["real impedance Z' [Ohm]"][num_random]))[:data_len+5],
                                imaginary_impedance = np.array(eval(data["imaginary impedance Z'' [Ohm]"][num_random]))[:data_len+5],
                                fitted_impedance= eval(data[fit_data][num_random]),
                                chi = data[chi][num_random],
                                suggested_circuit = data[custom_cicuit][num_random],
                                colorbar= False,
                                ax_sci_notation="both", scientific_limit=3,  scientific_label_colorbar=False,
                                legend_label=True, norm_color=True)
            eplot.ax.set(xlabel="", ylabel="")
            #divider = make_axes_locatable(ax)
            #cax = divider.append_axes('bottom', size='10%', pad=0.6)
            cbar_ax = fig.add_axes([1, 0.15, 0.05, 0.7])
            #cbar_ax.set_ylabel('f [Hz]',)
            fig.colorbar(im, cax=cbar_ax, fraction=0.046, pad=0.04, label='f [Hz]')

        if experiment_type == "arrhenius":
            exp_id = data["experimentID"][num_random]
            aplot.arrhenius_fit(subplot_ax = ax[i, j], temperatures = data["temperature [°C]"][data["experimentID"] == exp_id],
                                log_conductivity = data["log_conductivity"][data["experimentID"] == exp_id],
                                inverted_scale_temperatures= data["inverted_scale_temperatures"][data["experimentID"] == exp_id],
                                ln_conductivity_fit = data[ln_conductivity_fit][data["experimentID"] == exp_id],
                                activation = data[activation][data["experimentID"] == exp_id].values[0],
                                arrhenius_constant = data[arrhenius_constant][data["experimentID"] == exp_id].values[0],
                                r2_score = data[r2_score][data["experimentID"] == exp_id].values[0])

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
fig.text(-0.02, 0.85, 'Q1', va='center', rotation='vertical', fontsize=10)
fig.text(-0.02, 0.5, 'Q2', va='center', rotation='vertical', fontsize=10)
fig.text(-0.02, 0.15, 'Q3', va='center', rotation='vertical', fontsize = 10)
fig.text(0.5, -0.02, r"$\frac{1000}{T}$ $[K^{-1}]$", ha='center', fontsize = 10)
plt.savefig(os.path.join(os.getcwd(), fr"electrolyte_figures\error_{experiment_type}.svg"))

