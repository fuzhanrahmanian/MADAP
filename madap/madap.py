import argparse
import sys
from ast import arguments
import os
from utils import utils
import logger
from data_acquisition import data_acquisition as da
from echem.impedance import impedance
from echem.arrhenius import arrhenius
from echem.voltammetry import voltammetry
from pathlib import Path


log = logger.setup_applevel_logger(file_name = 'madap_debug.log')


def call_impedance(data, result_dir, plots, parser, args):
    """calling the impedance procedure and parse the corresponding arguments

    Args:
        data (class): the given data frame for analysis
    """

    # print("What is the name (or index) of the column of frequency (f [Hz]) ?")
    # freq_data = da.choose_options(data)

    # print("What is the name (or index) of the column of real impedance (Z' [Ω])?")
    # real_data = da.choose_options(data)

    # print("What is the name (or index) of the column of imaginary impedance (Z''[Ω]) ?")
    # imag_data = da.choose_options(data)

    # print("What is the name (or index) of the column of phase shift (\u03c6 [\u00b0]) (optional)? If no phase shift is required type 'n'")
    # phase_shift_data = da.choose_options(data)


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

    # TODO: Parser for Voltage
    print("what is the cell constant value? write n if it is not available")
    cell_constant = "n"
    # cell constant, voltage, suggested_circuit, initial_value


    procedure = impedance.EIS(Im, voltage=4, suggested_circuit="R0-p(R1,CPE1)", initial_value=[800, 1e+14, 1e-9, 0.8],
                              cell_constant=cell_constant)

    # TODO , write a parser and ask what circuit user will define
    # list of available elements : 's', 'C', 'Ws', 'K', 'W', 'Wo', 'R', 'p', 'L', 'TLMQ', 'CPE', 'G', 'La', 'T', 'Gs'
    # series or parallel
    #slog.info("")
    #circuit = ""
    # TODO : check if user gives any plot at all or not
    # find the according function in class impedance
    # either all the analysis at once or just read the specific function names

    if isinstance(plots, str):
        plots = [plots]
    if isinstance(plots, tuple):
        plots = list(plots)
    procedure.perform_all_actions(result_dir, plots=plots)
    # what functions/ procedure user wants


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
    # Parse the argument
    parser.add_argument("-s", "--selection", choices=["header", "specific"],help= "select whether you are choosing a header or a specific column & row in your data")
    args = parser.parse_known_args()[0]
    #args = parser.parse_args()

    # Acquire data
    data = da.acquire_data(args.data)
    log.info(f"the header of your data is: \n {data.head()}")
    result_dir = utils.create_dir(os.path.join(args.results, args.procedure))

    if args.procedure == "impedance":

        log.info("what plot do you want? optiions: nyquist, bode, nyquist_fit, residual")
        plots = "nyquist" ,"nyquist_fit", "residual", "bode"  #"nyquist_fit" #, "bode" #, "residual" # input()
        call_impedance(data, result_dir, plots, parser, args)

    elif args.procedure == "arrhenius":
        log.info("what plot do you want? options: arrhenius, arrhenius_fit")
        plots = "arrhenius", "arrhenius_fit" #,"arrhenius_fit" # input()
        call_arrhenius(data, result_dir, plots)
    elif args.procedure == "voltammetry": pass


if __name__ == "__main__":
    main()
