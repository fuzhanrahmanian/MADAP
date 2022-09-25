import sys, os
import json
from turtle import title
sys.path.append(os.path.join(os.getcwd(), "figures_creation"))
import paper_impedance_madap as pim
import pandas as pd
import glob
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import shutil
from PIL import Image
from PIL import ImageDraw, ImageFont
import numpy as np

DEFAUL_DATA = pd.read_csv(os.path.join(os.getcwd(),r"data/final_version_6.csv"), sep=";")

default_path = r"C:\Users\lucaz\OneDrive\Fuzhi\KIT\madap\data\default\impedance_madap"
custom_path = r"C:\Users\lucaz\OneDrive\Fuzhi\KIT\madap\data\custom\impedance_madap"

polished_path = r"C:\Users\lucaz\OneDrive\Fuzhi\KIT\madap\data\polished"

trial_path = r"C:\Repositories\MADAP\electrolyte_figures\impedance_trials"

start_row = 397  #sys.argv[1]
batch_selection = DEFAUL_DATA['experimentID'].unique()[start_row:start_row+1].tolist()

print(f"Batch selection: {batch_selection} with start row {start_row}")

temperatures = DEFAUL_DATA["temperature [°C]"].unique().tolist()
temperatures.sort()

#polished_data = pd.DataFrame(columns=["experimentID", "default", "custom", "retrain"])
#polished_data = pd.read_csv(os.path.join(polished_path, "polished_data.csv"), sep=";")
for exp_id in batch_selection:
    result = {}#{"experimentID": exp_id, "default": [], "custom": [], "retrain": []}
    result[exp_id] = {"default": [], "custom": [], "retrain": []}
    temperature_to_retrain = []
    for temp in temperatures:
        # Find plot in default and custom folder
        for plot_default, plot_custom in zip(glob.glob(os.path.join(default_path, "plots", f"*{exp_id}_{temp}*.png")), glob.glob(os.path.join(custom_path, "plots", f"*{exp_id}_{temp}*.png"))):
            im1 = Image.open(plot_default)
            draw = ImageDraw.Draw(im1)
            draw.text((700, 0),f"Default for temperature {temp}",(0,0,0), font=ImageFont.truetype("arial.ttf", 100))
            im2 = Image.open(plot_custom)
            draw = ImageDraw.Draw(im2)
            draw.text((700, 0),f"Custom for temperature {temp}",(0,0,0), font=ImageFont.truetype("arial.ttf", 100))

            Image.fromarray(np.hstack((np.array(im1),np.array(im2)))).show(title=f"Default, Custom for temp {temp}")

        action = input(f"Which one is better at temperature {temp} and exp_id {exp_id}? (Press c (custom), default(d) or Re-train(r))")

        if action == "c":
            # Add result to the dictionary
            result[exp_id]["custom"].append(temp)
            # Copy the plots
            for plots in glob.glob(os.path.join(custom_path, "plots", f"*{exp_id}_{temp}*")):
                shutil.copy(plots, os.path.join(polished_path, "plots"))
            for custom_file in glob.glob(os.path.join(custom_path, "data", f"*{exp_id}_{temp}*")):
                shutil.copy(custom_file, os.path.join(polished_path, "data"))
            print("Custom")
        elif action == "d":
            # Add result to the dictionary
            result[exp_id]["default"].append(temp)
            # Copy the plots
            for plots in glob.glob(os.path.join(default_path, "plots", f"*{exp_id}_{temp}*")):
                shutil.copy(plots, os.path.join(polished_path, "plots"))
            for default_file in glob.glob(os.path.join(default_path, "data", f"*{exp_id}_{temp}*")):
                shutil.copy(default_file, os.path.join(polished_path, "data"))
            print("Default")
        elif action == "r":
            # Add result to the dictionary
            result[exp_id]["retrain"].append(temp)
            temperature_to_retrain.append(temp)
            print("Re-train")


    print("Done with the temperatures")
    print("Now retraining the data")
    print(result)
    for temp_r in temperature_to_retrain:
        print(f"Retraining for temperature {temp_r}")
        good_case = False
        while not good_case:
            temperature_to_extract = input("From which temperature should the data be extracted?")
            data_file_to_extract = input("Which data file should be extracted? (c (Custom), d (default)")


            if data_file_to_extract == "c":
                file_name = glob.glob(os.path.join(custom_path, "data", f"*{exp_id}_{temperature_to_extract}*.json"))[0]
                json_data = json.load(open(os.path.join(custom_path, "data", file_name)))
                circuit = json_data["Circuit String"]
                parameters = json_data["Parameters"]

            elif data_file_to_extract == "d":
                file_name = glob.glob(os.path.join(default_path, "data", f"*{exp_id}_{temperature_to_extract}*.json"))[0]
                json_data = json.load(open(os.path.join(default_path, "data", file_name)))
                circuit = json_data["Circuit String"]
                parameters = json_data["Parameters"]

            print(f"Parameters are {parameters}")
            value_modification = input("Do you want to modify the initial resistance? (y/n)")
            if value_modification == "y":
                new_val = input("Enter the new resistance value")
                parameters[0] = float(new_val)
            # new_circuit = input("Do you want new ciruit string? (y/n)")
            # if new_circuit == "y":
                # new_circuit_string = input("Enter the new circuit string")
                # circuit = new_circuit_string
                # new_parameters = input("Enter new parameters")
                # parameters = eval(new_parameters)

                print(f"New parameters are {parameters}")

            pim.constly_compute(data=DEFAUL_DATA,exp_id=exp_id,temp=temp_r,params=parameters,circuit=circuit)
            im = Image.open(glob.glob(os.path.join(trial_path, "plots", f"*{exp_id}_{temp_r}*.png"))[0])
            draw = ImageDraw.Draw(im)
            draw.text((300, 0),f"Retrained with temp {temperature_to_extract} for temperature {temp_r}",(0,0,0), font=ImageFont.truetype("arial.ttf", 100))
            im.show()


            decision = input("Is this a good case? (y/n)")
            if decision == "y":
                good_case = True

                for plots in glob.glob(os.path.join(trial_path, "plots", f"*{exp_id}_{temp_r}*")):
                    shutil.move(plots, os.path.join(polished_path, "plots"))
                for default_file in glob.glob(os.path.join(trial_path, "data", f"*{exp_id}_{temp_r}*")):
                    shutil.move(default_file, os.path.join(polished_path, "data"))
            if decision == "n":
                good_case = False
                # Delete all subfolders folder trial_path
                shutil.rmtree(os.path.join(trial_path, "plots"))
                shutil.rmtree(os.path.join(trial_path, "data"))

    # with open (os.path.join(polished_path, "result.json"), "w") as f:
    #     json.dump(result, f)
    # # update an existing json file
    with open (os.path.join(polished_path, "result.json"), "r") as f:
        concat_result = json.load(f)
        concat_result.update(result)
    with open (os.path.join(polished_path, "result.json"), "w") as f:
        json.dump(concat_result, f)
