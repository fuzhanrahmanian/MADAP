import os
import pandas as pd

data = pd.read_csv(os.path.join(os.getcwd(),r"data/Dataframe_STRUCTURED_all508.csv"), sep=";")
del data["Unnamed: 0"]
data.groupby(["experimentID"]).size()

names_list = []
for index, row in data.iterrows():
    names_list.append(data["experimentID"][index][:-2])


repeated_experiment = {i:names_list.count(i) for i in names_list}

print(f"The minimun number of repetition is {min(repeated_experiment.values())/10} and the maximun is {max(repeated_experiment.values())/10}")