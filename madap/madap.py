import argparse
import logger
from data_acquisition import data_acquisition

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


if __name__ == "__main__":
    main()