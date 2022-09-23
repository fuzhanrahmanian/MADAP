import os
import pandas as pd

DEFAUL_DATA = pd.read_csv(os.path.join(os.getcwd(),r"data/final_version_6.csv"), sep=";")

default_path = r"C:\Users\fuzha\OneDrive\Fuzhi\KIT\madap\data\default\impedance_madap"
custom_path = r"C:\Users\fuzha\OneDrive\Fuzhi\KIT\madap\data\custom\impedance_madap"

start_row = 28
batch_selection = DEFAUL_DATA['experimentID'].unique()[start_row:]

json_default_files = [pos_json for pos_json in os.listdir(os.path.join(default_path,"data")) if pos_json.endswith('.json')]
csv_default_files = [pos_csv for pos_csv in os.listdir(os.path.join(default_path,"data")) if pos_csv.endswith('.csv')]

json_custom_files = [pos_json for pos_json in  os.listdir(os.path.join(custom_path,"data")) if pos_json.endswith('.json')]
csv_custom_files = [pos_csv for pos_csv in os.listdir(os.path.join(custom_path,"data")) if pos_csv.endswith('.csv')]

temperatures = DEFAUL_DATA["temperature [°C]"].unique().tolist()
temperatures.sort()


for exp_id in batch_selection:
    for temp in temperatures:
        pass


