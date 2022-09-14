import pandas as pd

path_to_data = r"data/Dataframe_STRUCTURED_all508.csv"

data = pd.read_csv(path_to_data, sep= ";")

expriment_id_of_choice = "PYA_30032021_BM067_4"
temperature_of_choice = -30.0
test_num = 7
selected_data = data[["frequency [Hz]", "real impedance Z' [Ohm]", "imaginary impedance Z'' [Ohm]"]][(data["experimentID"] == expriment_id_of_choice) & (data["temperature [°C]"] == temperature_of_choice)]

support_data = pd.DataFrame()
support_data = pd.concat([support_data, pd.Series(eval(selected_data["frequency [Hz]"].values[0])),
                    pd.Series(eval(selected_data["real impedance Z' [Ohm]"].values[0])),
                    pd.Series(eval(selected_data["imaginary impedance Z'' [Ohm]"].values[0]))], axis=1)

support_data.columns = "freq", "real", "imag"
support_data.to_csv(fr"C:\Repositories\MADAP\test\testfile\supported\test_imp_{test_num}.csv")