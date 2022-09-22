import os
import pandas as pd


data = pd.read_csv(os.path.join(os.getcwd(), r"data/Dataframe_STRUCTURED_all508.csv"), sep=";")
best_performed_data = pd.read_csv(os.path.join(os.getcwd(), r"data/comparison_data/resistance_best_analysis_default.csv"), sep=";")

processed_data_1 = pd.read_csv(os.path.join(os.getcwd(), r"data/arr_data/processed_data_arr_and_impedance_default_type2.csv"), sep=";")
processed_data_2 = pd.read_csv(os.path.join(os.getcwd(), r"data/arr_data/processed_data_arr_and_impedance_default_type4_random.csv"), sep=";")
#processed_data_3 = pd.read_csv(os.path.join(os.getcwd(), r"data/arr_data/processed_data_arr_and_impedance_customtype1.csv"), sep=";")
processed_data = {"default_type4_random": processed_data_2, "default_type2": processed_data_1}#, "customtype1": processed_data_3}


for i in range(len(data)):
    # find the best performed analysis
    analysis_type = best_performed_data.loc[i, "best_analysis"]
    extraction_source = processed_data[analysis_type]

    # get the experiment id of the best performed analysis
    exp_id = best_performed_data.loc[i, "experimentID"]
    temp = best_performed_data.loc[i, "temperature [°C]"]


    print(i)
    data.loc[(data["experimentID"] == exp_id) & (data["temperature [°C]"] == temp), f"madap_eis_conductivity [S/cm]"] = extraction_source.loc[(data["experimentID"] == exp_id) & (data["temperature [°C]"] == temp), f"madap_eis_conductivity_{analysis_type} [S/cm]"]
    #3. parameters plus theirs errors/confidance
    data.loc[(data["experimentID"] == exp_id) & (data["temperature [°C]"] == temp), f"madap_eis_fit_params"] = extraction_source.loc[(data["experimentID"] == exp_id) & (data["temperature [°C]"] == temp), f"madap_eis_fit_params_{analysis_type}"]
    #4. RMSE of the fit
    data.loc[(data["experimentID"] == exp_id) & (data["temperature [°C]"] == temp), f"madap_eis_rmse"] = extraction_source.loc[(data["experimentID"] == exp_id) & (data["temperature [°C]"] == temp), f"madap_eis_rmse_{analysis_type}"]
    #5. num_rc_linKK
    data.loc[(data["experimentID"] == exp_id) & (data["temperature [°C]"] == temp), f"madap_eis_num_rc_linKK"] = extraction_source.loc[(data["experimentID"] == exp_id) & (data["temperature [°C]"] == temp), f"madap_eis_num_rc_linKK_{analysis_type}"]
    #6. eval_fit_linKK
    data.loc[(data["experimentID"] == exp_id) & (data["temperature [°C]"] == temp), f"madap_eis_eval_fit_linKK"] = extraction_source.loc[(data["experimentID"] == exp_id) & (data["temperature [°C]"] == temp), f"madap_eis_eval_fit_linKK_{analysis_type}"]
    #7. resistance [Ohm]
    data.loc[(data["experimentID"] == exp_id) & (data["temperature [°C]"] == temp), f"madap_eis_resistance [Ohm]"] = extraction_source.loc[(data["experimentID"] == exp_id) & (data["temperature [°C]"] == temp), f"madap_eis_resistance_{analysis_type} [Ohm]"]
    #8 chi_value
    data.loc[(data["experimentID"] == exp_id) & (data["temperature [°C]"] == temp), f"madap_eis_chi_square"] = extraction_source.loc[(data["experimentID"] == exp_id) & (data["temperature [°C]"] == temp), f"madap_eis_chi_square_{analysis_type}"]
    # 9. fit
    data.loc[(data["experimentID"] == exp_id) & (data["temperature [°C]"] == temp), f"madap_eis_fit"] = extraction_source.loc[(data["experimentID"] == exp_id) & (data["temperature [°C]"] == temp), f"madap_eis_fit_{analysis_type}"]
    # custom circuit
    data.loc[(data["experimentID"] == exp_id) & (data["temperature [°C]"] == temp), f"madap_eis_custom_circuit"] = extraction_source.loc[(data["experimentID"] == exp_id) & (data["temperature [°C]"] == temp), f"madap_eis_custom_circuit_{analysis_type}"]
    # predicted datafit_impedance
    data.loc[(data["experimentID"] == exp_id) & (data["temperature [°C]"] == temp), f"madap_eis_predicted_impedance [Ohm]"] = extraction_source.loc[(data["experimentID"] == exp_id) & (data["temperature [°C]"] == temp), f"madap_eis_predicted_impedance_{analysis_type} [Ohm]"]
    # real residual
    data.loc[(data["experimentID"] == exp_id) & (data["temperature [°C]"] == temp), f"madap_eis_residual_real [Ohm]"] = extraction_source.loc[(data["experimentID"] == exp_id) & (data["temperature [°C]"] == temp), f"madap_eis_residual_real_{analysis_type} [Ohm]"]
    # imaginary residual
    data.loc[(data["experimentID"] == exp_id) & (data["temperature [°C]"] == temp), f"madap_eis_residual_imaginary [Ohm]"] = extraction_source.loc[(data["experimentID"] == exp_id) & (data["temperature [°C]"] == temp), f"madap_eis_residual_imaginary_{analysis_type} [Ohm]"]

    # 1. activation
    # data.loc[data["experimentID"] == exp_id, f"madap_arr_activation_energy [mJ/mol]"] = extraction_source.loc[extraction_source["experimentID"] == exp_id, f"madap_arr_activation_energy_{analysis_type} [mJ/mol]"]
    # # 2. cell constant
    # data.loc[data["experimentID"] == exp_id, f"madap_arr_activation_constant"] = extraction_source.loc[extraction_source["experimentID"] == exp_id, f"madap_arr_activation_constant_{analysis_type}"]
    # # 3. r2 score
    # data.loc[data["experimentID"] == exp_id, f"madap_arr_activation_r2_score"] = extraction_source.loc[extraction_source["experimentID"] == exp_id, f"madap_arr_activation_r2_score_{analysis_type}"]
    # # 4. mse score
    # data.loc[data["experimentID"] == exp_id, f"madap_arr_activation_mse"] = extraction_source.loc[extraction_source["experimentID"] == exp_id, f"madap_arr_activation_mse_{analysis_type}"]
    # # 7 fitted conductivity
    # data.loc[data["experimentID"] == exp_id, f"madap_arr_fitted_log_conductivity [ln(S/cm)]"] = extraction_source.loc[extraction_source["experimentID"] == exp_id, f"madap_arr_fitted_log_conductivity_{analysis_type} [ln(S/cm)]"]

# remove the unreliable data
data = data.drop(data[data["experimentID"] == "WOC_18012022_BM-K009_1"].index)
data = data.drop(data[data["experimentID"] == "WOC_18012022_BM-K009_3"].index)
data = data.drop(data[data["experimentID"] == "WOC_18012022_BM-K009_5"].index)
data = data.drop(data[data["experimentID"] == "WOC_18012022_BM-K009_8"].index)

data = data.reset_index()
del data["index"]
del data["Unnamed: 0"]
data.to_csv(os.path.join(os.getcwd(),fr"data/final_version_3.csv"), sep=";", index=True, mode='w+')
