import argparse
from secrets import choice
import sys
from ast import arguments
import os
from madap.utils import utils
from madap.logger import logger
from madap.data_acquisition import data_acquisition as da
<<<<<<< HEAD
from madap.echem.e_impedance import e_impedance
=======
from madap.echem.impedance import impedance
>>>>>>> e1ec172 (More work on the GUI)
from madap.echem.arrhenius import arrhenius
from madap.echem.voltammetry import voltammetry
from pathlib import Path


log = logger.setup_applevel_logger(file_name = 'madap_debug.log')

def _analyze_parser_args():
    """Private function to analyze the parser arguments

    Returns:
        argparse: The parser with correct arguments
    """
    first_parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter, add_help=False)
    # Options for procedure
    procedure = first_parser.add_argument_group("Options for the procedure")
    procedure.add_argument("-p", "--procedure", type=str, choices=['arrhenius', 'impedance', 'voltammetry'],
                          help="Procedure of the analysis")
    proc = first_parser.parse_known_args()[0]
    if proc.procedure == "impedance":
        procedure.add_argument("-ip", "--impedance_procedure", type=str, required=True, choices=['EIS', 'Mottschotcky', 'Lissajous'],
                            help="Which of the impedance procedures you want to use?")
        proc = first_parser.parse_known_args()[0]
        if proc.impedance_procedure == "EIS":
            eis = first_parser.add_argument_group("Options for the EIS procedure")
            # Add the arguments for the EIS procedure
            eis.add_argument("-pl", "--plots", required=True, choices=["nyquist" ,"nyquist_fit", "residual", "bode"],
                            nargs="+", help="plots to be generated")
            eis.add_argument("-v", "--voltage", type=float, required=False, default=None,
                            help="applied voltage [V] if applicable")
            eis.add_argument("-cc", "--cell_constant", type=float, required=False, default=None,
                            help="cell constant if applicable")
            eis.add_argument("-sc", "--suggested_circuit", type=str, required=False, default=None,
                            help="suggested circuit if applicable. \n Available elements are 's', 'C', 'Ws', 'K', 'W', 'Wo', 'R', \
                                'p', 'L', 'TLMQ', 'CPE', 'G', 'La', 'T', 'Gs' \n Parallel circuit can be defined like p(element1, element2)\
                                and the series circuit like element1_element2")
            eis.add_argument("-iv", "--initial_values", required=False, default=None,
                            help="initial values for the suggested circuit. \
                                \n format: element1, element2, ... \
                                \n it will be used just if the suggested_circuit is available.")
        elif proc.impedance_procedure == "Mottschotcky":
            # TODO
            pass
        elif proc.impedance_procedure == "Lissajous":
            # TODO
            pass

    elif proc.procedure == "arrhenius":
        arrhenius = first_parser.add_argument_group("Options for the Arrhenius procedure")
        arrhenius.add_argument("-pl", "--plots", choices=["arrhenius" ,"arrhenius_fit"],
                                nargs="+", required=True, help="Plots to be generated")

    elif proc.procedure == "voltammetry":
        voltammetry = first_parser.add_argument_group("Options for the Arrhenius procedure")
        voltammetry.add_argument("-vp", "--voltammetry_procedure", type=str, required=True,
                            choices=['cyclic_voltammetric', 'cyclic_amperometric', "cyclic_potentiometric"],)
        proc = first_parser.parse_known_args()[0]
        if proc.voltammetry_procedure == "cyclic_voltammetric":
            # TODO
            pass
        elif proc.voltammetry_procedure == "cyclic_amperometric":
            # TODO
            pass
        elif proc.voltammetry_procedure == "cyclic_potentiometric":
            # TODO
            pass

    # Options for data import
    data = first_parser.add_argument_group("Options for data import")
    data.add_argument("-f", "--file", type=Path, required=True, metavar="FILE", help="Path to the data file")
    data_selection = data.add_mutually_exclusive_group()
    data_selection.add_argument("-sp", "--specific", type=str, nargs="+",
                            help="row and column number of the frequency, real impedance, imaginary_impedance and phase shift \
                            \n write n if it is not applicable \n order is important.\n format: start_row,end_row,start_column,end_column \
                            \n 1,10,1,2 means rows 1 to 10 and columns 1 to 2")
    data_selection.add_argument("-hl", "--header_list", type=str, nargs="+",
                            help="Definitions of the headers for frequency [Hz], real impedance [\u2126],\
                            imaginary_impedance [\u2126] and phase shift \u03c6 [\u00b0] \n write n if it is not applicable \n order is important.")

    parser = argparse.ArgumentParser(description='Use MADAP for electrochemical analysis', parents=[first_parser],
                                    formatter_class=argparse.RawDescriptionHelpFormatter)
    # Options for results
    parser.add_argument("-r", "--results", type=Path, required=True, help="Directory for saving results")

    return parser


def call_impedance(data, result_dir, args):
    """calling the impedance procedure and parse the corresponding arguments

    Args:
        data (class): the given data frame for analysis
        result_dir (str): the directory for saving results
        args (parser.args): Parsed arguments
    """

    if args.header_list:
        # Check if args header is a list
<<<<<<< HEAD
        if isinstance(args.header_list, list):
            header_names = args.header_list[0].split(", ") if len(args.header_list) == 1 else args.header_list
        else:
            header_names = args.header_list

        phase_shift_data = None if len(header_names) == 3 else data[header_names[3]]

        freq_data, real_data, imag_data = data[header_names[0]],\
                                          data[header_names[1]],\
                                          data[header_names[2]]
    if args.specific:
        row_col = args.specific[0].split(", ")
        phase_shift_data = None if len(row_col) == 3 else da.select_data(data, row_col[3])
        freq_data, real_data, imag_data = da.select_data(data, row_col[0]), \
                                          da.select_data(data, row_col[1]), \
                                          da.select_data(data, row_col[2])

    Im = e_impedance.EImpedance(da.format_data(freq_data), da.format_data(real_data), da.format_data(imag_data), da.format_data(phase_shift_data))
=======
        if not isinstance(args.header_list, list):
            header_names = args.header_list[0].split(", ")
        else:
            header_names = args.header_list
        freq_data, real_data, imag_data, phase_shift_data = data[header_names[0]],\
                                                            data[header_names[1]],\
                                                            data[header_names[2]],\
                                                            data[header_names[3]] \
                                                            if header_names[3] != "n" else None
    if args.specific:
        row_col = args.specific[0].split(", ")
        freq_data, real_data, imag_data, phase_shift_data = da.select_data(data, row_col[0]), \
                                                            da.select_data(data, row_col[1]), \
                                                            da.select_data(data, row_col[2]), \
                                                            da.select_data(data, row_col[3]) \
                                                            if row_col[3] != "n" else None

    Im = impedance.Impedance(da.format_data(freq_data), da.format_data(real_data), da.format_data(imag_data), da.format_data(phase_shift_data))
>>>>>>> e1ec172 (More work on the GUI)

    if args.impedance_procedure == "EIS":
        log.info(f"The given voltage is {args.voltage} [V], cell constant is {args.cell_constant},\
                   suggested circuit is {args.suggested_circuit} and initial values are {args.initial_values}.")

        # Instantiate the procedure
<<<<<<< HEAD
        procedure = e_impedance.EIS(Im, voltage=args.voltage, suggested_circuit=args.suggested_circuit,
=======
        procedure = impedance.EIS(Im, voltage=args.voltage, suggested_circuit=args.suggested_circuit,
>>>>>>> e1ec172 (More work on the GUI)
                                  initial_value=eval(args.initial_values) if args.initial_values else None, cell_constant=args.cell_constant)

    elif args.impedance_procedure == "Mottschotcky":
        #TODO
        # # Instantiate the procedure
        pass
    elif args.impedance_procedure == "Lissajous":
        #TODO
        # # Instantiate the procedure
        pass

    # Format plots arguments
    plots = da.format_plots(args.plots)

    # Perform all actions
    procedure.perform_all_actions(result_dir, plots=plots)

<<<<<<< HEAD
    return procedure

=======
>>>>>>> e1ec172 (More work on the GUI)
def call_arrhenius(data, result_dir, args):
    """Calling the arrhenius procedure and parse the corresponding arguments

    Args:
        data (class): the given data frame for analysis
        result_dir (str): the directory for saving results
        args (parser.args): Parsed arguments
    """


    if args.header_list:
<<<<<<< HEAD
        if isinstance(args.header_list, list):
            header_names = args.header_list[0].split(", ") if len(args.header_list) == 1 else args.header_list
        else:
            header_names = args.header_list

=======
        header_names = args.header_list[0].split(", ")
>>>>>>> e1ec172 (More work on the GUI)
        temp_data, cond_data = data[header_names[0]], data[header_names[1]]
    if args.specific:
        row_col = args.specific[0].split(", ")
        temp_data, cond_data = da.select_data(data, row_col[0]), da.select_data(data, row_col[1])

    # Instantiate the procedure
    Arr = arrhenius.Arrhenius(da.format_data(temp_data), da.format_data(cond_data))

    # Format the plots arguments
    plots = da.format_plots(args.plots)

    # Perform all actions
    Arr.perform_all_actions(result_dir, plots = plots)

<<<<<<< HEAD
    return Arr

=======
>>>>>>> e1ec172 (More work on the GUI)
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

def start_procedure(args):
    """Function to prepare the data for analysis.
    It also prepares folder for results and plots.

    Args:
        args (object): Object containing arguments from parser or gui.
    """

    data = da.acquire_data(args.file)
    log.info(f"the header of your data is: \n {data.head()}")
    result_dir = utils.create_dir(os.path.join(args.results, args.procedure))

    if args.procedure in ["impedance", "Impedance"]:
<<<<<<< HEAD
        procedure = call_impedance(data, result_dir, args)

    elif args.procedure in ["arrhenius", "Arrhenius"]:
        procedure = call_arrhenius(data, result_dir, args)
=======
        call_impedance(data, result_dir, args)

    elif args.procedure == "arrhenius":
        call_arrhenius(data, result_dir, args)
>>>>>>> e1ec172 (More work on the GUI)

    elif args.procedure == "voltammetry":
        log.info("Voltammetrys is not supported at the moment. Exiting ...")
        exit()

<<<<<<< HEAD
    return procedure

=======
>>>>>>> e1ec172 (More work on the GUI)
def main():
    log.info("==================================WELCOME TO MADAP==================================")
    # Create the parser
    parser = _analyze_parser_args()
    # Parse the argument
    args = parser.parse_args()

    # Acquire data
    start_procedure(args)


if __name__ == "__main__":
    main()
