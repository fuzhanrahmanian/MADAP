import argparse
import logger
from data_acquisition import data_acquisition
from echem import impedance

log = logger.setup_applevel_logger(file_name = 'madap_debug.log')



def main():
    log.info("==================================WELCOME TO MADAP==================================")
    # Create the parser
    parser = argparse.ArgumentParser(description='Use MADAP for electrochemical analysis')
    # Add an argument
    parser.add_argument("-d", "--data", type=str, required=True, help="Path to the data")
    parser.add_argument("-p", "--procedure", type=str, choices=['arrhenius', 'impedance', 'voltammetry'],
                        required=True, help="Procedure of the analysis")
    # Parse the argument
    args = parser.parse_args()

    # Acquire data
    data = data_acquisition.acquire_data(args.data)
    
    # Ask user what is the column f/z/z1 (either name of column or number of column)
    if args.procedure == "impedance":
        print(data.head())
        log.info("What is the name (or index) of the column of frequency f?")
        freq_idx = "freq" # input()
        log.info("What is the name (or index) of the column of real impedance z'?")
        real_idx = "real" #input()
        log.info("What is the name (or index) of the column of imaginary impedance z''?")
        imag_idx = "imag" #input()
        log.info("What is the name (or index) of the column of phase shift (optional)? If no phase shift is required type 'n'")
        phase_shift = "n" #input()
        
        if phase_shift == "n":
            phase_shift = None
        imp = impedance.EIS(data, freq_idx=freq_idx, real_idx=real_idx, imag_idx=imag_idx, phase_shift=phase_shift)
        imp.plot()


if __name__ == "__main__":
    main()