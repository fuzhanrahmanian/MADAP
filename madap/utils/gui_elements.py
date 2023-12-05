""" Just a file containing some lengthy text used for the GUI helpers. """

HEADER_OR_SPECIFIC_HELP="If the data selection is 'Headers', insert the headers for: " \
                        "\nfrequency [Hz], real impedance [\u2126], imaginary impedance, phase shift \u03c6[\u00b0] (optional).Order is relevant.\n"\
                        "Example: 'freq, real, imag'" \
                        "\n \n"\
                        "If the data selection is 'Specific' insert the row and column numbers. Order is relevant." \
                        "\nFormat: 'start_row,end_row,start_column,end_column': 1,10,1,2  translates to rows 1 to 10 and columns 1 to 2."\
                        "\nExample: '0,40,0,1; 0,40,1,2; 0,40,2,3'"

SUGGESTED_CIRCUIT_HELP="Suggested circuit (optional).\n" \
                        "Available circuit elements are: 's', 'C', 'Ws', 'K', 'W', 'Wo', 'R'," \
                        "'p', 'L', 'TLMQ', 'CPE', 'G', 'La', 'T', 'Gs'." \
                        "\nParallel circuit can be defined as p(element1, element2) " \
                        "and the series circuit like element1_element2."\
                        "\nFormat: R0-p(R1,CPE1)"

INITIAL_VALUES_HELP="Initial values for the suggested circuit." \
                    "\nIt will be used just if the suggested circuit was defined. " \
                    "\nFormat: [element1, element2, ...], i.e.: [800,1e+14,1e-9,0.8] "


VOLTAGE_HELP="Applied voltage (optional)"

CELL_CONSTANT_HELP="Cell constant (optional)"

UPPER_LIMIT_QUANTILE_HELP="Upper limit quantile (optional)."

LOWER_LIMIT_QUANTILE_HELP="Lower limit quantile (optional)."

WINDOW_SIZE_HELP="Window size for the best linear fit for getting diffusion coefficient and reaction rate constant (optional)."

APPLIED_CURRENT_HELP = "Applied current (optional)."

PENALTY_VALUE_HELP = "Penalty value for finding the inflection point or peak points (optional)."

MEASURED_CURRENT_UNITS_HELP = "The unit in which the current is measured."

MEASURED_TIME_UNITS_HELP = "The unit in which the time is measured."
