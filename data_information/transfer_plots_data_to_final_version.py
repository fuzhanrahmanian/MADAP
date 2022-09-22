import shutil
import os
import sys
import pandas as pd

test_type = "impedance" # arrhenius, impedance
data = pd.read_csv(os.path.join(os.getcwd(), r"data/final_version_3.csv"), sep=";")
best_performed_data = pd.read_csv(os.path.join(os.getcwd(), r"data/comparison_data/resistance_best_analysis_default.csv"), sep=";")

analysis_type = "default_type4_random" #["default_type2", "customtype1", "default_type4_random"]

def retrieve_file_name(test_type, analysis_type):
    path_to_data = fr"C:\Users\Fuzhan\Repositories\MADAP\electrolyte_figures\{test_type}_{analysis_type}\data"
    path_to_plot = fr"C:\Users\Fuzhan\Repositories\MADAP\electrolyte_figures\{test_type}_{analysis_type}\plots"

    json_files = [pos_json for pos_json in os.listdir(path_to_data) if pos_json.endswith('.json')]
    csv_files = [pos_csv for pos_csv in os.listdir(path_to_data) if pos_csv.endswith('.csv')]
    plot_files_png = [pos_plot for pos_plot in os.listdir(path_to_plot) if pos_plot.endswith('.png')]
    plot_files_svg = [pos_plot for pos_plot in os.listdir(path_to_plot) if pos_plot.endswith('.svg')]

    return json_files, csv_files, plot_files_png, plot_files_svg

def make_id_impedance(file):
    splitted_file = file.split("_")
    experimentid_name = f"{splitted_file[2]}_{splitted_file[3]}_{splitted_file[4]}_{splitted_file[5]}_{splitted_file[6]}"
    return experimentid_name


jsons, csvs, plots_png, plots_svg = retrieve_file_name(test_type, analysis_type)
if test_type == "impedance":
    json_ids, csv_ids, plot_png_ids, plots_svg_ids = [make_id_impedance(file) for file in jsons], [make_id_impedance(file) for file in csvs], [make_id_impedance(file) for file in plots_png], [make_id_impedance(file) for file in plots_svg]



for i in range(len(data)):
    # get the experimentID
    experiment_ID = data.iloc[i]["experimentID"]
    print(experiment_ID)
    if test_type == "impedance":
        temperature = data.iloc[i]["temperature [°C]"]
        mode_type = best_performed_data.loc[best_performed_data["experimentID"] == experiment_ID, "best_analysis"].values[0]
        if mode_type == analysis_type:

            json_index = json_ids.index(f"{experiment_ID}_{temperature}")
            orgin_json = fr"C:\Users\Fuzhan\Repositories\MADAP\electrolyte_figures\{test_type}_{analysis_type}\data\{jsons[json_index]}"

            csv_index = csv_ids.index(f"{experiment_ID}_{temperature}")
            origin_csv = fr"C:\Users\Fuzhan\Repositories\MADAP\electrolyte_figures\{test_type}_{analysis_type}\data\{csvs[csv_index]}"

            plot_index_png = plot_png_ids.index(f"{experiment_ID}_{temperature}")
            origin_plots_png = fr"C:\Users\Fuzhan\Repositories\MADAP\electrolyte_figures\{test_type}_{analysis_type}\plots\{plots_png[plot_index_png]}"

            plot_index_svg = plot_png_ids.index(f"{experiment_ID}_{temperature}")
            origin_plots_svg = fr"C:\Users\Fuzhan\Repositories\MADAP\electrolyte_figures\{test_type}_{analysis_type}\plots\{plots_svg[plot_index_svg]}"

            final_json = fr"C:\Users\Fuzhan\Repositories\MADAP\electrolyte_figures\final_version\data\{jsons[json_index]}"
            final_csv = fr"C:\Users\Fuzhan\Repositories\MADAP\electrolyte_figures\final_version\data\{csvs[csv_index]}"
            final_plot_png = fr"C:\Users\Fuzhan\Repositories\MADAP\electrolyte_figures\final_version\plots\{plots_png[plot_index_png]}"
            final_plot_svg = fr"C:\Users\Fuzhan\Repositories\MADAP\electrolyte_figures\final_version\plots\{plots_svg[plot_index_svg]}"

            shutil.move(orgin_json, final_json)
            shutil.move(origin_csv, final_csv)
            shutil.move(origin_plots_png, final_plot_png)
            shutil.move(origin_plots_svg, final_plot_svg)

