import argparse
from secrets import choice
import sys
from ast import arguments
import os

from traitlets import default
from utils import utils
import logger
from data_acquisition import data_acquisition as da
from echem.impedance import impedance
from echem.arrhenius import arrhenius
from echem.voltammetry import voltammetry
from pathlib import Path


log = logger.setup_applevel_logger(file_name = 'madap_debug.log')


def call_impedance(data, result_dir, parser, args):
    """calling the impedance procedure and parse the corresponding arguments

    Args:
        data (class): the given data frame for analysis
    """

    if args.selection == "header":
        parser.add_argument("-n", "--name_list", type=str, nargs="+",
                                            help="name of the headers for frequency, real impedance, imaginary_impedance and phase shift \n write n if it is not applicable \n order is important.")
        args = parser.parse_known_args()[0]
        header_names = args.name_list[0].split(", ")
        freq_data, real_data, imag_data, phase_shift_data = data[header_names[0]], data[header_names[1]], data[header_names[2]], data[header_names[3]] if header_names[3] != "n" else None

    else:
        parser.add_argument("-rc", "--row_column", type=str, nargs="+",
                            help="row and column number of the frequency, real impedance, imaginary_impedance and phase shift \n write n if it is not applicable \n order is important.\n format: start_row,end_row,start_column,end_column \n 1,10,1,2 means rows 1 to 10 and columns 1 to 2")
        args = parser.parse_known_args()[0]
        header_names = args.row_column[0].split(", ")
        freq_data, real_data, imag_data, phase_shift_data = da.select_data(data, header_names[0]), da.select_data(data, header_names[1]), da.select_data(data, header_names[2]), da.select_data(data, header_names[3]) if header_names[3] != "n" else None

    Im = impedance.Impedance(da.format_data(freq_data), da.format_data(real_data), da.format_data(imag_data), da.format_data(phase_shift_data))

    if args.impedance_procedure == "EIS":

        parser.add_argument("-v", "--voltage", type=float, required=False, default=None, help="applied voltage if applicable")
        parser.add_argument("-cc", "--cell_constant", type=float, required=False, default=None, help="cell constant if applicable")
        parser.add_argument("-sc", "--suggested_circuit", type=str, required=False, default=None, help="suggested circuit if applicable. \n Available elements are 's', 'C', 'Ws', 'K', 'W', 'Wo', 'R', 'p', 'L', 'TLMQ', 'CPE', 'G', 'La', 'T', 'Gs' \n Parallel circuit can be defined like p(element1, element2) and the series circuit like element1_element2")
        parser.add_argument("-iv", "--initial_values", required=False, default=None,
                            help="initial values for the suggested circuit. \n format: element1, element2, ... \n it will be used just if the suggested_circuit is available.")

        parser.add_argument("-pl", "--plots", required=True, choices=["nyquist" ,"nyquist_fit", "residual", "bode"], nargs="+", help="plots to be generated")

        args = parser.parse_args()
        log.info(f"The given voltage is {args.voltage} [V], cell constant is {args.cell_constant}, suggested circuit is {args.suggested_circuit} and initial values are {args.initial_values}.")


        procedure = impedance.EIS(Im, voltage=args.voltage, suggested_circuit=args.suggested_circuit, initial_value=eval(args.initial_values),
                                cell_constant=args.cell_constant)

    elif args.impedance_procedure == "Mottschotcky":
        #TODO
        pass
    elif args.impedance_procedure == "Lissajous":
        #TODO
        pass

    plots = da.format_plots(args.plots)
    procedure.perform_all_actions(result_dir, plots=plots)


def call_arrhenius(data, result_dir, plots):
    log.info("What is the name (or index) of the column of temperature (T [\u00b0C]) ?")
    # TODO
    temp_idx = "temp" #input()
    # TODO
    log.info("What is the name (or index) of the column of conductivity (\u03b1 [S/cm]) ?")
    conductivity_idx = "cond" #input()
    Arr = arrhenius.Arrhenius(da.format_data(data[temp_idx]), da.format_data(data[conductivity_idx]))
    if isinstance(plots, str):
        plots = [plots]
    if isinstance(plots, tuple):
        plots = list(plots)
    Arr.perform_all_actions(result_dir, plots=plots)

def call_voltammetry(data, result_dir, plots):
    log.info("What is the name (or index) of the column of voltage (v [V]) ?")
    # TODO
    voltage_idx = "voltage" #input()
    # TODO
    log.info("What is the name (or index) of the column of current (I [A]) ?")
    current_idx = "current" #input()
    # TODO
    log.info("What is the name (or index) of the column of time (t [s]) ?")
    time_idx = "time" #input()

    Arr = voltammetry.Voltammetry(da.format_data(data[voltage_idx]), da.format_data(data[current_idx]),
                                da.format_data(data[time_idx]))
    if isinstance(plots, str):
        plots = [plots]
    if isinstance(plots, tuple):
        plots = list(plots)
    Arr.perform_all_actions(result_dir, plots=plots)



def main():
    log.info("==================================WELCOME TO MADAP==================================")
    # Create the parser
    parser = argparse.ArgumentParser(description='Use MADAP for electrochemical analysis')
    # Add an argument
    parser.add_argument("-d", "--data", type=str, required=True, help="Path to the data")
    parser.add_argument("-p", "--procedure", type=str, choices=['arrhenius', 'impedance', 'voltammetry'],
                        required=True, help="Procedure of the analysis")
    parser.add_argument("-r", "--results", type=Path, required=True, help="Directory for saving results")

    parser.add_argument("-s", "--selection", choices=["header", "specific"],help= "select whether you are choosing a header or a specific column & row in your data")
    # Parse the argument
    args = parser.parse_known_args()[0]

    # Acquire data
    data = da.acquire_data(args.data)
    log.info(f"the header of your data is: \n {data.head()}")
    result_dir = utils.create_dir(os.path.join(args.results, args.procedure))

    if args.procedure == "impedance":
        parser.add_argument("-ip", "--impedance_procedure", type=str, required=True ,choices=['EIS', 'Mottschotcky', 'Lissajous'],
                            help="Which of the impedance procedures you want to use?")

        #log.info("what plot do you want? optiions: nyquist, bode, nyquist_fit, residual")
        #plots = "nyquist" ,"nyquist_fit", "residual", "bode"  #"nyquist_fit" #, "bode" #, "residual" # input()
        call_impedance(data, result_dir, parser, args)

    elif args.procedure == "arrhenius":
        log.info("what plot do you want? options: arrhenius, arrhenius_fit")
        plots = "arrhenius", "arrhenius_fit" #,"arrhenius_fit" # input()
        call_arrhenius(data, result_dir, plots)
    elif args.procedure == "voltammetry": pass


if __name__ == "__main__":
    main()
