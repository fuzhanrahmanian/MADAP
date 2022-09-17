import os
import pandas as pd

data = pd.read_csv(os.path.join(os.getcwd(),r"data/finalized_version.csv"), sep=";")
PHASESHIFT = True
NULLVARIABLES= False


if PHASESHIFT:
    # Correct the phase shift data type:
    for i in range(len(data)):
        data[data.columns[14]].iloc[i] = data[data.columns[14]].iloc[i].replace(" ", ",").replace(",,", ",").replace("\r\n", "").replace("[,", "[")

    print(data[data.columns[14]].iloc[0])

    data.to_csv(os.path.join(os.getcwd(),fr"data/final_version_4.csv"), sep=";", index=True, mode='w+')

if NULLVARIABLES:
    # remove the amplitude, bias, error, GD and range from the original data as they contain of zero values
    del data["amplitude [-]"]
    del data["bias"]
    del data["GD"]
    del data["error"]
    del data["range"]
    del data["Unnamed: 0"]
    data.to_csv(os.path.join(os.getcwd(),fr"data/final_version_4.csv"), sep=";", index=True, mode='w+')
