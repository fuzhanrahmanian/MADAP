import os
import pandas as pd

data = pd.read_csv(os.path.join(os.getcwd(),r"data/Dataframe_STRUCTURED_all508_editted.csv"), sep=";")
PHASESHIFT = False
NULLVARIABLES= True


if PHASESHIFT:
    # Correct the phase shift data type:
    for i in range(len(data)):
        data[data.columns[19]].iloc[i] = data[data.columns[19]].iloc[i].replace(" ", ",").replace(",,", ",").replace("\r\n", "").replace("[,", "[")

    print(data[data.columns[19]].iloc[0])

    data.to_csv(os.path.join(os.getcwd(),fr"data/Dataframe_STRUCTURED_all508_editted.csv"), sep=";", index=True, mode='w+')

if NULLVARIABLES:
    # remove the amplitude, bias, error, GD and range from the original data as they contain of zero values
    del data["amplitude [-]"]
    del data["bias"]
    del data["GD"]
    del data["error"]
    del data["range"]
    del data["Unnamed: 0"]
    data.to_csv(os.path.join(os.getcwd(),fr"data/Dataframe_STRUCTURED_all508_editted_nozero.csv"), sep=";", index=True, mode='w+')
