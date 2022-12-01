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

MOLARVOLUME_HELP="Molar volume of the electrode in cm^3/mol"

CHARGENUMBER_HELP="Charge number of the intercalating species."

CONTACTAREA_HELP="Contact area of the electrode with the electrolyte in cm^2"

def plotting_element(subparser, plots):
    """ Adds an element to the GUI for plotting the data.

    Args:
        subparser (GooeyParser): Subparser to add the element to.
        plots (list): List of plot types.
    """
    subparser.add_argument("-pl", "--plots", metavar="Plots", required=True, choices=plots,
                             nargs="+", help="Plots to be generated", widget="Listbox")

def data_import_element(subparser):
    """ Adds an element to the GUI for importing the data.

    Args:
        subparser (GooeyParser): Subparser to add the element to.
    """
    # Procedure subgroup
    data = subparser.add_argument_group("Data import",
                                        gooey_options={'show_border': True, 'columns': 1})

    # Procedure - File
    file = data.add_argument_group("File selection", gooey_options={'show_border': True})
    file.add_argument("-f", "--file", type=str, required=True,
                      metavar="File containing the dataset", help="Path to the data file",
                      widget="FileChooser")

    # Procedure - File - Data Selection
    file_data = data.add_argument_group("Data Selection (select one)", gooey_options={
         'show_border': True,
         'columns': 1
     })
    file_data.add_argument("-ds", "--data-selection", choices=["Headers", "Specific"],
                           required=True, metavar="Data Selection",
                           help="Select all data (by header) or specific data", widget="Dropdown")
    file_data.add_argument("-dl", "--data-list", type=str, required=False,
                           metavar="Headers or Specific", help=HEADER_OR_SPECIFIC_HELP)
