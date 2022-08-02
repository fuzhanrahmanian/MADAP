"Concatinating the available two datasets"
import sys
import os
sys.path.append(os.path.abspath(os.path.join(
    os.path.dirname(__file__), os.path.pardir)))

import pandas as pd

data_first_set = pd.read_csv(os.path.join(os.getcwd(),r"data/OriginalDataRaw.csv"), sep=";")
data_second_set = pd.read_csv(os.path.join(os.getcwd(),r"data/ElectrolytepredictionAfterOneShotRaw.csv"), sep=";")

data_all = pd.DataFrame(columns=data_first_set.columns)

# concat first and second set of data to data_all
data_all = pd.concat([data_all, data_first_set, data_second_set], ignore_index=True)
del data_all["Unnamed: 0"]

# save complete data to csv for further analysis
data_all.to_csv(os.path.join(os.getcwd(),r"data/CompleteData.csv"), sep=";", index=True)