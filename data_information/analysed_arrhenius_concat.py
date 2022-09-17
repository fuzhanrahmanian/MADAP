import os, json
import pandas as pd

# path can be changed
analysis_type = "madap" #["default_type1", "default_type2", "default_type3", "customtype1", "default_type4_random", default_christian]

path_to_json = fr"C:\Users\Fuzhan\Repositories\MADAP\electrolyte_figures\arrhenius_{analysis_type}\data"
json_files = [pos_json for pos_json in os.listdir(path_to_json) if pos_json.endswith('.json')]
csv_files = [pos_csv for pos_csv in os.listdir(path_to_json) if pos_csv.endswith('.csv')]

# open the processed data with eis
if (analysis_type != "default_christian") and (analysis_type != "madap"):
    processed_data_imp = pd.read_csv(os.path.join(os.getcwd(),fr"data/imp_data/processed_data_impedance_{analysis_type}.csv"), sep=";")
if analysis_type == "default_christian":
    processed_data_imp = pd.read_csv(os.path.join(os.getcwd(),r"data/Dataframe_STRUCTURED_all508.csv"), sep=";")
if analysis_type == "madap":
    processed_data_imp = pd.read_csv(os.path.join(os.getcwd(),r"data/final_version_4.csv"), sep=";")
del processed_data_imp['Unnamed: 0']

processed_data = processed_data_imp.copy()

def concat_new_data(data, exp_id, json_file, csv_file, analysis_type = "default"):
    # 1. activation
    data.loc[data["experimentID"] == exp_id, f"madap_arr_activation_energy_{analysis_type} [mJ/mol]"] = json_file["activation [mJ/mol]"]
    # 2. cell constant
    data.loc[data["experimentID"] == exp_id, f"madap_arr_activation_constant_{analysis_type}"] = json_file["arr_constant [S.cm⁻¹]"]
    # 3. r2 score
    data.loc[data["experimentID"] == exp_id, f"madap_arr_activation_r2_score_{analysis_type}"] = json_file["R2_score"]
    # 4. mse score
    data.loc[data["experimentID"] == exp_id, f"madap_arr_activation_mse_{analysis_type}"] = json_file["MSE"]
    # 5. log conductivity
    #data.loc[data["experimentID"] == exp_id, f"madap_arr_log_conductivity_{analysis_type}"] = csv_file["log_conductivty [ln(S/cm)]"]
    # 6. inverted scale temperature
    #data.loc[data["experimentID"] == exp_id, f"madap_arr_inverted_scale_temperature_{analysis_type} [1000/K]"] = csv_file["inverted_scale_temperatures [1000/K]"]
    # 7 fitted conductivity
    data.loc[data["experimentID"] == exp_id, f"madap_arr_fitted_log_conductivity_{analysis_type} [ln(S/cm)]"] = csv_file["log_conductivity_fit [ln(S/cm)]"].values


for i, file in enumerate(zip(json_files, csv_files)):

    # open the json file
    json_file = json.load(open(f"{path_to_json}\{file[0]}", encoding="utf8"))
    # open the csv file
    csv_file = pd.read_csv(fr"{path_to_json}/{file[1]}")

    # get the names for saving to the main dataset
    splitted_file = file[0].split("_")
    experimentid_name = f"{splitted_file[2]}_{splitted_file[3]}_{splitted_file[4]}_{splitted_file[5]}"
    temperature = splitted_file[6]
    # add the analysed value to the raw data
    concat_new_data(data = processed_data, exp_id = experimentid_name, json_file = json_file, csv_file = csv_file, analysis_type = analysis_type)


processed_data.to_csv(os.path.join(os.getcwd(),fr"data/final_version_5.csv"), sep=";", index=True, mode='w+')
