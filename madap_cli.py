""" This module is the main entry point for MADAP. It defines the CLI to be used by the user."""
import argparse
import os
import re
from pathlib import Path

import pandas as pd

from madap.data_acquisition import data_acquisition as da
from madap.echem.arrhenius import arrhenius
from madap.echem.e_impedance import e_impedance
from madap.echem.voltammetry import (voltammetry_CA, voltammetry_CP,
                                     voltammetry_CV)
from madap.logger import logger
from madap.utils import utils

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
        arrhenius_pars = first_parser.add_argument_group("Options for the Arrhenius procedure")
        arrhenius_pars.add_argument("-pl", "--plots", choices=["arrhenius" ,"arrhenius_fit"],
                                nargs="+", required=True, help="Plots to be generated")

    elif proc.procedure == "voltammetry":
        voltammetry_pars = first_parser.add_argument_group("Options for the Arrhenius procedure")
        voltammetry_pars.add_argument("-vp", "--voltammetry_procedure", type=str, required=True,
                            choices=['CV', 'CA', "CP"],)
        voltammetry_pars.add_argument("-mc", "--measured_current_units", type=str, required=True,
                            default="uA", choices=["uA", "mA", "A"], help="Measured current units")
        voltammetry_pars.add_argument("-mt", "--measured_time_units", type=str, required=False,
                            default="s", choices=["ms", "s", "min", "h"], help="Measured time units")
        voltammetry_pars.add_argument("-ne", "--number_of_electrons", type=int, required=False,
                            default=1, help="Number of electrons involved in the reaction")
        voltammetry_pars.add_argument("-cam", "--concentration_of_active_material", type=float, required=False,
                            default=None, help="Concentration of the active material [mol/cm^3]")
        voltammetry_pars.add_argument("-mam", "--mass_of_active_material", type=float, required=False,
                            default=None, help="Mass of the active material [g]")
        voltammetry_pars.add_argument("-ea", "--electrode_area", type=float, required=False,
                            default=None, help="Electrode area [cm^2]")
        proc = first_parser.parse_known_args()[0]
        if proc.voltammetry_procedure == "CV":
            cv = first_parser.add_argument_group("Options for the CV procedure")
            cv.add_argument("-plcy", "--cycle_list", required=False, default=None,
                            help="list of cycles to be plotted. \n format: [1, 2, 3] \n if it is not specified, all cycles will be plotted")
            cv.add_argument("-pl", "--plots", required=True, choices=["E-t", "I-t", "Peak Scan", "CV", "Tafel"],
                            nargs="+", help="plots to be generated")
            cv.add_argument("-temp", "--temperature", type=float, required=False, default=None,
                            help="temperature [K] if applicable")
            cv.add_argument("-w", "--window_size", type=int, required=True, default=1, help="window size for the moving average")
            cv.add_argument("-sc", "--applied_scan_rate", type=float, required=False, default=0.1,
                            help="Applied scan rate [V/s] if applicable. Default is 0.1 V/s")
        elif proc.voltammetry_procedure == "CA":
            ca = first_parser.add_argument_group("Options for the CA procedure")
            ca.add_argument("-pl", "--plots", required=True, choices=["CA", "Log_CA", "CC", "Cottrell", "Anson", "Voltage"],
                            nargs="+", help="plots to be generated")
            ca.add_argument("-a", "--applied_voltage", type=float, required=False, default=None,
                            help="applied voltage [V] if applicable")
            ca.add_argument("-w", "--window_size", type=int, required=False, default=None, help="window size for the moving average")
        elif proc.voltammetry_procedure == "CP":
            cp = first_parser.add_argument_group("Options for the CP procedure")
            cp.add_argument("-pl", "--plots", required=True, \
                choices=["CP", "CC", "Cottrell", "Voltage_Profile", "Potential_Rate", "Differential_Capacity"],
                            nargs="+", help="plots to be generated")
            cp.add_argument("-ap", "--applied_potential", type=float, required=False, default=None,
                            help="applied potential [V] if applicable")
            cp.add_argument("-pv", "--penalty_value", type=float, required=False, default=None,
                            help="penalty value for the regularization")

    # Options for data import
    data = first_parser.add_argument_group("Options for data import")
    data.add_argument("-f", "--file", type=Path, required=True, metavar="FILE", help="Path to the data file")
    data.add_argument("-u", "--upper_limit_quantile", type=float, required=False,
                      default=0.99, help="Upper quantile for detecting the outliers in data")
    data.add_argument("-l", "--lower_limit_quantile", type=float, required=False,
                      default=0.01, help="Lower quantile for detecting the outliers in data")
    data_selection = data.add_mutually_exclusive_group()
    data_selection.add_argument("-sp", "--specific", type=str, nargs="+",
                            help="row and column number of the frequency, real impedance, \
                            imaginary_impedance and phase shift \
                            \n write n if it is not applicable \n order is important.\
                            \n format: start_row,end_row,start_column,end_column \
                            \n 1,10,1,2 means rows 1 to 10 and columns 1 to 2")
    data_selection.add_argument("-hl", "--header_list", type=str, nargs="+",
                            help="Definitions of the headers for frequency [Hz], \
                            real impedance [\u2126],\
                            imaginary_impedance [\u2126] and phase shift \u03c6 [\u00b0] \
                            \n write n if it is not applicable \n order is important.")

    parser = argparse.ArgumentParser(description='Use MADAP for electrochemical analysis',
                                     parents=[first_parser],
                                    formatter_class=argparse.RawDescriptionHelpFormatter)
    # Options for results
    parser.add_argument("-r", "--results", type=Path, required=True,
                        help="Directory for saving results")

    return parser


def call_impedance(data, result_dir, args):
    """calling the impedance procedure and parse the corresponding arguments

    Args:
        data (class): the given data frame for analysiswrite
        result_dir (str): the directory for saving results
        args (parser.args): Parsed arguments
    """

    if args.header_list:
        # Check if args header is a list
        if isinstance(args.header_list, list):
            header_names = args.header_list[0].split(", ") if len(args.header_list) == 1 else \
            args.header_list
        else:
            header_names = args.header_list

        phase_shift_data = None if len(header_names) == 3 else data[header_names[3]]

        _, nan_indices = da.remove_outlier_specifying_quantile(df = data,
                                                           columns = [header_names[1],
                                                                       header_names[2]],
                                                           low_quantile = args.lower_limit_quantile,
                                                           high_quantile = args.upper_limit_quantile)
        # remove nan rows
        data = da.remove_nan_rows(data, nan_indices)
        # extracting the data
        freq_data, real_data, imag_data = data[header_names[0]],\
                                          data[header_names[1]],\
                                          data[header_names[2]]

    if args.specific:

        try:
            if len(args.specific) >= 3:
                row_col = args.specific
            else:
                row_col = re.split('; |;', args.specific[0])

        except ValueError as e:
            log.error("The format of the specific data is not correct. Please check the help.")
            raise e

        selected_data = data.iloc[int(row_col[0].split(',')[0]): int(row_col[0].split(',')[1]), :]


        phase_shift_data = None if len(row_col) == 3 else da.select_data(data, row_col[3])


        freq_data, real_data, imag_data = da.select_data(selected_data, row_col[0]), \
                                          da.select_data(selected_data, row_col[1]), \
                                          da.select_data(selected_data, row_col[2])

        unprocessed_data = pd.DataFrame({"freq": freq_data, "real": real_data, "imag": imag_data})

        _, nan_indices = da.remove_outlier_specifying_quantile(df = unprocessed_data,
                                            columns = ["real", "imag"],
                                            low_quantile = args.lower_limit_quantile,
                                            high_quantile = args.upper_limit_quantile)

        data = da.remove_nan_rows(unprocessed_data, nan_indices)
        freq_data, real_data, imag_data = data["freq"], data["real"], data["imag"]

    impedance = e_impedance.EImpedance(da.format_data(freq_data), da.format_data(real_data),
                                da.format_data(imag_data), da.format_data(phase_shift_data))

    if args.impedance_procedure == "EIS":
        log.info(f"The given voltage is {args.voltage} [V], cell constant is {args.cell_constant},\
                   suggested circuit is {args.suggested_circuit} \
                   and initial values are {args.initial_values}.")

        # Instantiate the procedure
        procedure = e_impedance.EIS(impedance, voltage=args.voltage,
                                    suggested_circuit=args.suggested_circuit,
                                    initial_value=eval(args.initial_values)
                                    if args.initial_values else None,
                                    cell_constant=args.cell_constant)

    elif args.impedance_procedure == "Mottschotcky":
        #TODO
        # # Instantiate the procedure
        pass
    elif args.impedance_procedure == "Lissajous":
        #TODO
        # # Instantiate the procedure
        pass

    # Format plots arguments
    plots = da.format_list(args.plots)

    # Perform all actions
    procedure.perform_all_actions(result_dir, plots=plots)

    return procedure

def call_arrhenius(data, result_dir, args):
    """Calling the arrhenius procedure and parse the corresponding arguments

    Args:
        data (class): the given data frame for analysis
        result_dir (str): the directory for saving results
        args (parser.args): Parsed arguments
    """


    if args.header_list:
        if isinstance(args.header_list, list):
            header_names = args.header_list[0].split(", ") if len(args.header_list) == 1 else \
            args.header_list
        else:
            header_names = args.header_list

        temp_data, cond_data = data[header_names[0]], data[header_names[1]]
    if args.specific:

        try:
            if len(args.specific) == 2:
                row_col = args.specific
            else:
                row_col = re.split('; |;', args.specific[0])

        except ValueError as e:
            log.error("The format of the specific data is not correct. Please check the help.")
            raise e

        selected_data = data.iloc[int(row_col[0].split(',')[0]): int(row_col[0].split(',')[1]), :]

        #row_col = args.specific[0].split(", ")

        temp_data, cond_data = da.select_data(selected_data, row_col[0]), \
                               da.select_data(selected_data, row_col[1])
        if (not isinstance(temp_data, pd.Series)) and (not isinstance(cond_data, pd.Series)):
            temp_data, cond_data = pd.Series(temp_data).astype(float), pd.Series(cond_data).astype(float)
    # Instantiate the procedure
    arrhenius_cls = arrhenius.Arrhenius(da.format_data(temp_data), da.format_data(cond_data))

    # Format the plots arguments
    plots = da.format_list(args.plots)

    # Perform all actions
    arrhenius_cls.perform_all_actions(result_dir, plots = plots)

    return arrhenius_cls

def call_voltammetry(data, result_dir, args):
    """ Calling the voltammetry procedure and parse the corresponding arguments

    Args:
        data (class): the given data frame for analysis
        result_dir (str): the directory for saving results
        plots (list): list of plots to be generated
    """
    if args.header_list:
        # Check if args header is a list
        if isinstance(args.header_list, list):
            header_names = args.header_list[0].split(", ") if len(args.header_list) == 1 else \
            args.header_list
        else:
            header_names = args.header_list

        
        if len(header_names) == 2:
            current_data, voltage_data = data[header_names[0]], data[header_names[1]]
            time_data = None
            unavailable_plots = []
            # Define unavailable plots based on voltammetry procedure
            if args.voltammetry_procedure == "CV":
                unavailable_plots = ["E-t", "I-t", "Peak Scan"]
                # Tafel analysis might be limited without time data
                if "Tafel" in args.plots:
                    log.warning("Tafel analysis may be limited without time data.")
            elif args.voltammetry_procedure == "CA":
                unavailable_plots = ["CA", "Log_CA", "CC", "Cottrell", "Anson"]
            elif args.voltammetry_procedure == "CP":
                unavailable_plots = ["CP", "CC", "Cottrell", "Potential_Rate"]
            
            # Check if any requested plots are unavailable
            unavailable_requested = [plot for plot in args.plots if plot in unavailable_plots]
            if unavailable_requested:
                log.warning(f"The following plots are not available without time data: {unavailable_requested}")
                log.info("Will proceed with generating available plots only.")
            
        elif len(header_names) == 3:
            # extracting the data
            current_data, voltage_data, time_data = data[header_names[0]],\
                                                    data[header_names[1]],\
                                                    data[header_names[2]]

    if len(header_names) == 4:
        charge_data = da.format_data(data[header_names[3]])
    else:
        charge_data = None
    cycle_list = da.format_list(eval(args.cycle_list)) if args.cycle_list else None

    if args.voltammetry_procedure == "CA":
        voltammetry_cls = voltammetry_CA.Voltammetry_CA(current=da.format_data(current_data),
                                                        voltage=da.format_data(voltage_data),
                                                        time =da.format_data(time_data),
                                                        charge=charge_data,
                                                        args=args)
    if args.voltammetry_procedure == "CV":
        voltammetry_cls = voltammetry_CV.Voltammetry_CV(current=da.format_data(current_data),
                                                        voltage=da.format_data(voltage_data),
                                                        time_params =da.format_data(time_data),
                                                        scan_rate=charge_data,
                                                        cycle_list=cycle_list,
                                                        args=args)
    if args.voltammetry_procedure == "CP":
        voltammetry_cls = voltammetry_CP.Voltammetry_CP(current=da.format_data(current_data),
                                                        voltage=da.format_data(voltage_data),
                                                        time =da.format_data(time_data),
                                                        charge=charge_data,
                                                        args=args)

    # Format plots arguments and filter out unavailable plots if time_data is None
    plots = da.format_list(args.plots)
    if time_data is None:
        if args.voltammetry_procedure == "cv":
            unavailable_plots = ["E-t", "I-t", "Peak Scan"]
        elif args.voltammetry_procedure == "ca":
            unavailable_plots = ["CA", "Log_CA", "CC", "Cottrell", "Anson"]
        elif args.voltammetry_procedure == "cp":
            unavailable_plots = ["CP", "CC", "Cottrell", "Potential_Rate"]
        
        # Filter out unavailable plots
        plots = [plot for plot in plots if plot not in unavailable_plots]
        
        if not plots:
            log.error("All requested plots require time data which is not available.")
            raise ValueError("No available plots to generate. Please provide time data or select plots that don't require it.")
    
    try:
        voltammetry_cls.perform_all_actions(result_dir, plots=plots)
    except ValueError as e:
        log.error("The plot you selected is not available. Please check the help.")
        raise e
    return voltammetry_cls


def start_procedure(args):
    """Function to prepare the data for analysis.
    It also prepares folder for results and plots.

    Args:
        args (object): Object containing arguments from parser or gui.
    """

    data = da.acquire_data(args.file)
    da.remove_unnamed_col(data)
    log.info(f"the header of your data is: \n {data.head()}")
    result_dir = utils.create_dir(os.path.join(args.results, args.procedure))

    if args.procedure in ["impedance", "Impedance"]:
        procedure = call_impedance(data, result_dir, args)

    elif args.procedure in ["arrhenius", "Arrhenius"]:
        procedure = call_arrhenius(data, result_dir, args)

    elif args.procedure in ["voltammetry", "Voltammetry"]:
        procedure = call_voltammetry(data, result_dir, args)
    log.info("==================================DONE==================================")
    return procedure

def main():
    """Main function to start the program.
    """
    log.info("==================================WELCOME TO MADAP==================================")
    # Create the parser
    parser = _analyze_parser_args()
    # Parse the argument
    args = parser.parse_args()

    # Acquire data
    start_procedure(args)


if __name__ == "__main__":
    main()
