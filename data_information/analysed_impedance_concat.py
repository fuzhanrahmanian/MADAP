import os, json
import pandas as pd
import numpy as np

# path can be changed
analysis_type = "default_initial" #["default", "custom", "default_initial", "defualt_initial_outliers", "custom_outliers"]

path_to_json = fr"C:\Users\Fuzhan\Repositories\MADAP\electrolyte_figures\impedance_{analysis_type}\data"
json_files = [pos_json for pos_json in os.listdir(path_to_json) if pos_json.endswith('.json')]
csv_files = [pos_csv for pos_csv in os.listdir(path_to_json) if pos_csv.endswith('.csv')]
#
# open the raw_data
raw_data = pd.read_csv(os.path.join(os.getcwd(),r"data/Dataframe_STRUCTURED_all508.csv"), sep=";")
del raw_data['Unnamed: 0']


processed_data = raw_data.copy()

def concat_new_data(data, exp_id, temp, json_file, csv_file, analysis_type = "default"):
    #1. phaseshift should be there
    #2. conductivity
    data.loc[(data["experimentID"] == exp_id) & (data["temperature [°C]"] == float(temp)), f"madap_eis_conductivity_{analysis_type} [S/cm]"] = json_file["conductivity [S/cm]"]
    #3. parameters plus theirs errors/confidance
    data.loc[(data["experimentID"] == exp_id) & (data["temperature [°C]"] == float(temp)), f"madap_eis_fit_params_{analysis_type}"] = str([(val, err) for val, err in zip(json_file["Parameters"], json_file["Confidence"])])
    #4. RMSE of the fit
    data.loc[(data["experimentID"] == exp_id) & (data["temperature [°C]"] == float(temp)), f"madap_eis_rmse_{analysis_type}"] = json_file["RMSE_fit_error"]
    #5. num_rc_linKK
    data.loc[(data["experimentID"] == exp_id) & (data["temperature [°C]"] == float(temp)), f"madap_eis_num_rc_linKK_{analysis_type}"] = json_file["rc_linKK"]
    #6. eval_fit_linKK
    data.loc[(data["experimentID"] == exp_id) & (data["temperature [°C]"] == float(temp)), f"madap_eis_eval_fit_linKK_{analysis_type}"] = json_file["eval_fit_linKK"]
    #7. resistance [Ohm]
    data.loc[(data["experimentID"] == exp_id) & (data["temperature [°C]"] == float(temp)), f"madap_eis_resistance_{analysis_type} [Ohm]"]=  json_file["Parameters"][0]
    #8 chi_value
    data.loc[(data["experimentID"] == exp_id) & (data["temperature [°C]"] == float(temp)), f"madap_eis_chi_square_{analysis_type}"] = json_file["chi_square"]
    # 9. fit
    data.loc[(data["experimentID"] == exp_id) & (data["temperature [°C]"] == float(temp)), f"madap_eis_fit_{analysis_type}"] = str(json_file["Fit"])
    # custom circuit
    data.loc[(data["experimentID"] == exp_id) & (data["temperature [°C]"] == float(temp)), f"madap_eis_custom_circuit_{analysis_type}"] = json_file["Circuit String"]
    # predicted datafit_impedance
    data.loc[(data["experimentID"] == exp_id) & (data["temperature [°C]"] == float(temp)), f"madap_eis_predicted_impedance_{analysis_type} [Ohm]"] = str([eval(csv_file["fit_impedance [Ω]"][i]) for i, _ in enumerate(csv_file["fit_impedance [Ω]"][~csv_file["fit_impedance [Ω]"].isnull()])])
    # real residual
    data.loc[(data["experimentID"] == exp_id) & (data["temperature [°C]"] == float(temp)), f"madap_eis_residual_real_{analysis_type} [Ohm]"] = str([eval(csv_file["residual_real"][i]) for i, _ in enumerate(csv_file["residual_real"])])
    # imaginary residual
    data.loc[(data["experimentID"] == exp_id) & (data["temperature [°C]"] == float(temp)), f"madap_eis_residual_imaginary_{analysis_type} [Ohm]"] = str([eval(csv_file["residual_real"][i]) for i, _ in enumerate(csv_file["residual_imag"])])

    return data

for i, file in enumerate(zip(json_files, csv_files)):
    print(i)
    # open the json file
    json_file = json.load(open(fr"{path_to_json}/{file[0]}"))
    # open the csv file
    csv_file = pd.read_csv(fr"{path_to_json}/{file[1]}")

    # get the names for saving to the main dataset
    splitted_file = file[0].split("_")
    experimentid_name = f"{splitted_file[2]}_{splitted_file[3]}_{splitted_file[4]}_{splitted_file[5]}"
    temperature = splitted_file[6]
    # add the analysed value to the raw data
    processed_data = concat_new_data(processed_data, experimentid_name, temperature, json_file, csv_file, analysis_type)


processed_data.to_csv(os.path.join(os.getcwd(),fr"data/processed_data_impedance_{analysis_type}.csv"), sep=";", index=True, mode='w+')
