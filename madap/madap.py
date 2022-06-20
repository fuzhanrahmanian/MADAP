import argparse
import os
from utils import utils
import logger
from data_acquisition import data_acquisition as da
from echem.impedance import impedance
from pathlib import Path


log = logger.setup_applevel_logger(file_name = 'madap_debug.log')


def call_impedance(data, result_dir, plots):
    """calling the impedance procedure and parse the corresponding arguments

    Args:
        data (class): the given data frame for analysis
    """

    log.info("What is the name (or index) of the column of frequency (f [Hz]) ?")
    # TODO : specify the part of the dataset that we want to specify
    freq_idx = "freq" # input()
    log.info("What is the name (or index) of the column of real impedance (Z' [Ω])?")
    # TODO
    real_idx = "real" #input()
    log.info("What is the name (or index) of the column of imaginary impedance (Z''[Ω]) ?")
    # TODO
    imag_idx = "imag" #input()
    log.info("What is the name (or index) of the column of phase shift (\u03c6 [\u00b0]) (optional)? If no phase shift is required type 'n'")
    # TODO
    phase_shift = "n" #input()
    # TODO: Parser for Voltage
    cell_constant = "n"

    if phase_shift == "n":
        phase_shift = da.calculate_phaseshift(data[imag_idx], data[real_idx])
    
    Im = impedance.Impedance(da.format_data(data[freq_idx]), da.format_data(data[real_idx]),
                                da.format_data(data[imag_idx]), phase_shift)
    procedure = impedance.EIS(Im, voltage=4, suggested_circuit="R0-p(R1,CPE1)", initial_value=[800, 1e+14, 1e-9, 0.8], 
                              cell_constant=None)
    procedure.perform_all_actions(result_dir, plots=[plots])
    # what functions/ procedure user wants

    # TODO , write a parser and ask what circuit user will define
    # list of available elements : 's', 'C', 'Ws', 'K', 'W', 'Wo', 'R', 'p', 'L', 'TLMQ', 'CPE', 'G', 'La', 'T', 'Gs'
    # series or parallel
    log.info("")
    circuit = ""
    # TODO : check if user gives any plot at all or not
    # find the according function in class impedance
    # either all the analysis at once or just read the specific function names

def call_arrhenius(data):pass
def call_voltammetry(data):pass

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
    args = parser.parse_args()

    # Acquire data
    data = da.acquire_data(args.data)
    #print(data.head())
    result_dir = utils.create_dir(os.path.join(args.results, args.procedure))

    if args.procedure == "impedance":
        log.info("what plot do you want? optiions: nyquist, bode, nyquist_fit, residual")
        plots = "nyquist" # input()
        call_impedance(data, result_dir, plots)

    elif args.procedure == "arrhenius": pass

    elif args.procedure == "voltammetry": pass


if __name__ == "__main__":
    main()
