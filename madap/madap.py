import os
import argparse
import logger
import csv

log = logger.setup_applevel_logger(file_name = 'madap_debug.log')


def main():

    # Create the parser
    parser = argparse.ArgumentParser(description='Use MADAP for electrochemical analysis')
    # Add an argument
    parser.add_argument("--data", type=str, required=True, help="Path to the data")
    parser.add_argument("--procedure", type=str, choices=['arrhenius', 'impedance', 'voltammetry'],
                        required=True, help="Procedure of the analysis")

    # Parse the argument
    args = parser.parse_args()

    _ , extension = os.path.splitext(args.data)
    if extension == ".csv":
        log.info("Opening .csv file")
        file = open(args.data)
        exit()

if __name__ == "__main__":
    main()