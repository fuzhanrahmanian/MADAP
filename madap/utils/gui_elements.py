# Just a file containing some lengthy text
HEADER_OR_SPECIFIC_HELP="If the data selection is 'Headers', insert the headers for: " \
                        "\n - frequency [Hz] \n - real impedance [\u2126] \n - imaginary_impedance [\u2126] \n - phase shift \u03c6 [\u00b0]. \n" \
                        "Example: 'freq, real, imag, n'" \
                        "\n \n"\
                        "If the data selection is 'Specific' insert Row and column number.\n " \
                        "Format:\n 'start_row,end_row,start_column,end_column': 1,10,1,2 translates to rows 1 to 10 and columns 1 to 2.\n" \
                        "Example: '0,40,0,1, 0,40,1,2, 0,40,2,3, n'\n" \
                        "\n \n"\
                        "Write 'n' if it is not applicable. Order is relevant. "

SUGGESTED_CIRCUIT_HELP="Suggested circuit if applicable.\n" \
                        "Available circuit elements are 's', 'C', 'Ws', 'K', 'W', 'Wo', 'R'," \
                        "'p', 'L', 'TLMQ', 'CPE', 'G', 'La', 'T', 'Gs'.\n" \
                        "Parallel circuit can be defined as p(element1, element2)" \
                        "and the series circuit like element1_element2, i.e. : R0-p(R1,CPE1)"

INITIAL_VALUES_HELP="Initial values for the suggested circuit." \
                    "\nFormat: element1, element2, ..." \
                    "\nIt will be used just if the suggested_circuit is available, i.e.: [800,1e+14,1e-9,0.8] "

VOLTAGE_HELP="Applied voltage if applicable"

CELL_CONSTANT_HELP="Cell constant if applicable"


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
    data = subparser.add_argument_group("Data import", gooey_options={'show_border': True, 'columns': 1})

    # Procedure - File
    file = data.add_argument_group("File selection", gooey_options={'show_border': True})
    file.add_argument("-f", "--file", type=str, required=True, metavar="File containing the dataset", help="Path to the data file", widget="FileChooser")

    # Procedure - File - Data Selection
    file_data = data.add_argument_group("Data Selection (select one)", gooey_options={
         'show_border': True,
         'columns': 1
     })
    file_data.add_argument("-ds", "--data-selection", choices=["Headers", "Specific"], required=True, metavar="Data Selection", help="Select all data (by header) or specific data", widget="Dropdown")
    file_data.add_argument("-dl", "--data-list", type=str, required=False, metavar="Headers or Specific", help=HEADER_OR_SPECIFIC_HELP)
