"""This module implements the GUI application for MADAP """
import io

import PySimpleGUI as sg
import matplotlib.pyplot as plt

from matplotlib.backends.backend_tkagg import FigureCanvasAgg

from madap.utils import gui_elements
from madap_cli import start_procedure
class MadapGui:
    """This class implements the GUI application for MADAP
    """
    eis_plots = ["nyquist" ,"nyquist_fit", "residual", "bode"]
    arrhenius_plots = ["arrhenius", "arrhenius_fit"]

    def __init__(self):
        self.procedure = "Impedance"
        self.impedance_procedure= "EIS"
        self.file = None
        self.results = None
        self.header_list = None
        self.specific= None
        self.plots = None
        self.voltage = None
        self.cell_constant = None
        self.suggested_circuit = None
        self.initial_values = None
        self.upper_limit_quantile = None
        self.lower_limit_quantile = None

    # pylint: disable=inconsistent-return-statements
    def validate_fields(self):
        """ This function validates the fields in the GUI

        Returns:
            bool: Returns false if any of the fields are invalid.
        """
        if self.file == '':
            sg.popup_error('The data path is empty. Select a supported dataset file.', title='Input Error')
            return False
        if self.results == '':
            sg.popup_error('The result path is empty. Select a location for the results.', title='Input Error')
            return False
        if self.plots == []:
            sg.popup_error('Select the desired plot(s).', title='Input Error')
            return False
        if self.procedure == 'Impedance':
            if self.header_list and (len(self.header_list) not in [3,4]):
                sg.popup_error('Wrong number of header inputs.', title='Input Error')
                return False
            if self.specific and (len(self.specific) not in [3,4]):
                sg.popup_error('Wrong number of specific inputs.', title='Input Error')
                return False
        if self.procedure == 'Arrhenius':
            if self.header_list and (len(self.header_list) != 2):
                sg.popup_error('Wrong number of header inputs.', title='Input Error')
                return False
            if self.specific and (len(self.specific) != 2):
                sg.popup_error('Wrong number of specific inputs.', title='Input Error')
                return False
        return True


def draw_figure(element, figure):
    """
    Draws the previously created "figure" in the supplied Image Element

    Args:
        element (PySimpleGUI.Image): The image element to draw the figure on
        figure (matplotlib.figure.Figure): The figure to draw
    """

    plt.close('all')  # erases previously drawn plots
    figure.set_dpi(120)
    canv = FigureCanvasAgg(figure)
    buf = io.BytesIO()
    canv.print_figure(buf, format='png')
    if buf is None:
        return None
    buf.seek(0)
    element.update(data=buf.read())
    return canv


def gui_layout(madap, colors):
    """ This function creates the layout of the GUI

    Args:
        madap (MadapGui): The MadapGui object
        colors (dict): The colors of the GUI

    Returns:
        list: The layout of the layout of the GUI
    """

    # ----------- Create a layout with 3 buttons for the different procedures ----------- #
    layout_buttons = [[ sg.Button("Impedance", key="-BUT_Impedance-", button_color=('white', 'black')),
                        sg.Button("Arrhenius", key="-BUT_Arrhenius-", button_color=colors),
                        sg.Button("Voltammetry", key="-BUT_Voltammetry-", button_color=colors),
                        sg.Button("Pulse", key="-BUT_Pulse-", button_color=colors)]]

    # ----------- Create a layout with a field for a data path and a result path ----------- #
    layout_data = [[sg.Text('Data Path', size=(10, 1)), sg.InputText(key='-DATA_PATH-',
                                                                     size=(55,1)),
                    sg.FileBrowse(key='-BROWSE_DATA_PATH-')],
                   [sg.Text('Result Path', size=(10, 1)), sg.InputText(key='-RESULT_PATH-',
                                                                       size=(55,1)),
                    sg.FolderBrowse(key='-BROWSE_RESULT_PATH-')],
                ]

    # ----------- Create a layout with a field for a data selection options ----------- #
    layout_data_selection = [[sg.Text('Headers or specific',justification='left', font=("Arial", 13))],
                             [sg.Combo(['Headers', 'Specific Region'], key='-HEADER_OR_SPECIFIC-',
                                       default_value='Headers')],
                             [sg.InputText(key='-HEADER_OR_SPECIFIC_VALUE-',
                                           tooltip=gui_elements.HEADER_OR_SPECIFIC_HELP,
                                           default_text="freq, real, imag")]]


    # ----------- Create tabs for Impedance procedure ----------- #
    # pylint: disable=unnecessary-comprehension
    tab_layout_eis = [[sg.Text('This are the parameters for the EIS procedure')],
                    [sg.Text('Voltage (optional)',justification='left', font=("Arial", 13),
                             pad=(1,(20,0)))],
                    [ sg.InputText(key="-voltage-", tooltip=gui_elements.VOLTAGE_HELP, enable_events=True),
                     sg.Text('[V]')],
                    [sg.Text('Cell constant (optional)',justification='left', font=("Arial", 13),
                             pad=(1,(20,0)))],
                    [sg.InputText(key="-cell_constant-", tooltip=gui_elements.CELL_CONSTANT_HELP,
                                  enable_events=True), sg.Text('[1/cm]')],
                    [sg.Text("Upper limit of quantile (optional)",justification='left',
                             font=("Arial", 13), pad=(1,(20,0)))],
                    [sg.InputText(key="-upper_limit_quantile-", tooltip=gui_elements.UPPER_LIMIT_QUANTILE_HELP,
                                  enable_events=True, default_text="0.99")],
                    [sg.Text("Lower limit of quantile (optional)",justification='left',
                             font=("Arial", 13), pad=(1,(20,0)))],
                    [sg.InputText(key="-lower_limit_quantile-", tooltip=gui_elements.LOWER_LIMIT_QUANTILE_HELP,
                                  enable_events=True, default_text="0.01")],
                    [sg.Text('Suggested Circuit',justification='left', font=("Arial", 13),
                             pad=(1,(20,0)))],
                    [sg.InputText(key="-suggested_circuit-", tooltip=gui_elements.SUGGESTED_CIRCUIT_HELP,
                                  default_text="R0-p(R1,CPE1)")],
                    [sg.Text('Initial Value', justification='left', font=("Arial", 13), pad=(1,(20,0)))],
                    [sg.InputText(key="-initial_value-", enable_events=True, tooltip=gui_elements.INITIAL_VALUES_HELP,
                                  default_text="[860, 3e+5, 1e-09, 0.90]")],
                    [sg.Text('Plots',justification='left', font=("Arial", 13), pad=(1,(20,0)))],
                    [sg.Listbox([x for x in madap.eis_plots], key='-PLOTS_Impedance-',
                                size=(50,len(madap.eis_plots)), select_mode=sg.SELECT_MODE_MULTIPLE,
                                expand_x=True, expand_y=True)]]

    tab_layout_liss = [[sg.Text('This is inside Lissajous')],
                [sg.Input(key='-inLiss-')]]

    tab_layout_mott = [[sg.Text('This is inside Mottschosky')],
                    [sg.Input(key='-inMott-')]]

    # ----------- Layout the Impedance Options (Three TABS) ----------- #
    layout_impedance = [[sg.TabGroup(
                        [[sg.Tab('EIS', tab_layout_eis, key='-TAB_EIS-', expand_y=True),
                        sg.Tab('Lissajous', tab_layout_liss,  background_color='darkred',
                               key='-TAB_Lissajous-', expand_y=True),
                        sg.Tab('Mottschosky', tab_layout_mott, background_color='darkgreen',
                               key='-TAB_Mottschosky-', expand_y=True)]],
                        tab_location='topleft', selected_title_color='black', enable_events=True,
                        expand_y=True)]]

    # ----------- Layout the Arrhenius Options ----------- #
    layout_arrhenius = [[sg.Text('This are the parameters for the Arrhenius procedure')],
                        [sg.Text('Plots',justification='left', font=("Arial", 13), pad=(1,(20,0)))],
                        [sg.Listbox([x for x in madap.arrhenius_plots], key='-PLOTS_Arrhenius-',
                                    size=(50,len(madap.arrhenius_plots)+1),
                                    select_mode=sg.SELECT_MODE_MULTIPLE, expand_x=True,
                                    expand_y=True)]]

    # ----------- TODO Layout the Voltammetry Options ----------- #
    layout_voltammetry = [[sg.Text('This is Voltammetry')]]


    # ----------- TODO Layout the Pulse Options ----------- VOlTAGE_HELP ???#
    layout_pulse = [[sg.Text('This are the parameters for the GITT procedure')],
                    [sg.Text('Molar Volume',justification='left', font=("Arial", 13),
                             pad=(1,(20,0)))],
                    [ sg.InputText(key="-molarVolume-", tooltip=gui_elements.VOLTAGE_HELP, enable_events=True),
                     sg.Text('[cm^3/mol]')],
                    [sg.Text('Charge number of the intercalating species.',justification='left', font=("Arial", 13),
                             pad=(1,(20,0)))],
                    [sg.Text("Elektrode/Electrolyte contact area",justification='left',
                             font=("Arial", 13), pad=(1,(20,0)))],
                    [ sg.InputText(key="-contactarea-", tooltip=gui_elements.VOLTAGE_HELP, enable_events=True),
                        sg.Text('[cm^2]')],
                    [ sg.InputText(key="-chargenumber-", tooltip=gui_elements.VOLTAGE_HELP, enable_events=True),
                     sg.Text('')]
                    ]
    # ----------- Assemble the Procedure Column Element with the three layouts ----------- #
    procedure_column = [[sg.Column(layout_impedance, key='-COL_Impedance-', scrollable=True,
                                   vertical_scroll_only=True, expand_x=True, expand_y=True),
                        sg.Column(layout_arrhenius, visible=False, key='-COL_Arrhenius-',
                                  scrollable=True, vertical_scroll_only=True, expand_x=True,
                                  expand_y=True),
                        sg.Column(layout_voltammetry, visible=False, key='-COL_Voltammetry-',
                                  scrollable=True, vertical_scroll_only=True, expand_x=True,
                                  expand_y=True),
                        sg.Column(layout_pulse, visible=False, key='-COL_Pulse-',
                                  scrollable=True, vertical_scroll_only=True, expand_x=True,
                                  expand_y=True)]]           


    # ----------- Assemble the left Column Element ----------- #
    col1 = sg.Column([[sg.Frame('Data Selection:', layout_data_selection, font=("Arial", 15),
                                size=(550, 120), expand_y=True)],
                      [sg.Frame('Methods:', procedure_column, font=("Arial", 15), size=(550, 630),
                                expand_y=True)]],
                      expand_x=True, expand_y=True)

    # ----------- Layout the right Column Element ----------- #
    col2 = sg.Column([[sg.Frame('Plots:', [[sg.Image(key='-IMAGE-')]], visible=False,
                                key='-COL_PLOTS-')]])

    # ----------- Assemble the main layout ----------- #
    layout = [
        [layout_buttons],
        [layout_data],
        [col1, col2],
        [sg.Text('',justification='left', font=("Arial", 13), pad=(1,(20,0)), key='-LOG-',
                 enable_events=True)],
        [sg.Button('RUN'), sg.Button('EXIT')]]

    return layout


def main():
    """Main function of the GUI
    """

    # Select a theme
    sg.theme("LightGreen6")

    # Create class with initial values
    madap_gui = MadapGui()

    # Get primary colors and assemble window
    colors = (sg.theme_text_color(), sg.theme_background_color())
    layout = gui_layout(madap_gui, colors)
    title = 'MADAP: Modular Automatic Data Analysis Platform'
    window = sg.Window(title, layout, resizable=True)
    # Event loop
    while True:
        event, values = window.read()
        print(event, values)
        if event in (sg.WIN_CLOSED, 'EXIT'):
            break
        if event in ['-BUT_Impedance-', '-BUT_Arrhenius-', '-BUT_Voltammetry-', '-BUT_Pulse-']:
            event = event.strip('-BUT_')
            window[f'-COL_{madap_gui.procedure}-'].update(visible=False)
            window[f'-BUT_{madap_gui.procedure}-'].update(button_color=colors)
            window[f'-COL_{event}-'].update(visible=True)
            window[f'-BUT_{event}-'].update(button_color=('white', 'black'))
            madap_gui.procedure = event
        if values[0] in ['-TAB_EIS-', '-TAB_Lissajous-', '-TAB_Mottschotcky-']:
            madap_gui.impedance_procedure = values[0].strip('-TAB_')

        # Prevent the user from inoutting a value that is not a number in the voltage, cell constant and initial_value input field
        if event == '-voltage-' and len(values['-voltage-']) \
                                and values['-voltage-'][-1] not in '012345678890,.':
            window['-voltage-'].update(values['-voltage-'][:-1])
        if event == '-cell_constant-' and len(values['-cell_constant-']) \
                                      and values['-cell_constant-'][-1] not in '012345678890,.':
            window['-cell_constant-'].update(values['-cell_constant-'][:-1])
        if event == '-upper_limit_quantile-' and len(values['-upper_limit_quantile-']) \
                                             and values['-upper_limit_quantile-'][-1] not in '012345678890,.':
            window['-upper_limit_quantile-'].update(values['-upper_limit_quantile-'][:-1])
        if event == '-lower_limit_quantile-' and len(values['-lower_limit_quantile-']) \
                                             and values['-lower_limit_quantile-'][-1] not in '012345678890,.':
            window['-lower_limit_quantile-'].update(values['-lower_limit_quantile-'][:-1])

        if event == '-initial_value-' and len(values['-initial_value-']) \
                                      and values['-initial_value-'][-1] not in '012345678890,.e-+[]':
            window['-initial_value-'].update(values['-initial_value-'][:-1])
        if event == 'RUN':
            window['-LOG-'].update('Starting procedure...')
            madap_gui.file = values['-DATA_PATH-']
            madap_gui.results = values['-RESULT_PATH-']
            madap_gui.plots = values[f'-PLOTS_{madap_gui.procedure}-']
            madap_gui.voltage = values['-voltage-']
            madap_gui.cell_constant = values['-cell_constant-']
            madap_gui.suggested_circuit = values['-suggested_circuit-'] \
                                          if not values['-suggested_circuit-'] == '' else None
            madap_gui.initial_values = values['-initial_value-'] \
                                          if not values['-initial_value-'] == '' else None
            madap_gui.upper_limit_quantile = values['-upper_limit_quantile-'] \
                                          if not values['-upper_limit_quantile-'] == '' else None
            madap_gui.lower_limit_quantile = values['-lower_limit_quantile-'] \
                                          if not values['-lower_limit_quantile-'] == '' else None

            if values['-HEADER_OR_SPECIFIC-'] == 'Headers':
                madap_gui.specific = None
                madap_gui.header_list = values['-HEADER_OR_SPECIFIC_VALUE-'].replace(" ","")
                madap_gui.header_list = list(madap_gui.header_list.split(','))
            else:
                madap_gui.header_list = None
                madap_gui.specific = values['-HEADER_OR_SPECIFIC_VALUE-'].replace(" ","")
                madap_gui.specific = list(madap_gui.specific.split(';'))

            # Validate the fields
            validation = madap_gui.validate_fields()
            if not validation:
                window['-LOG-'].update('Inputs were not valid! Try again.')
                continue
            try:
                procedure = start_procedure(madap_gui)
            except Exception as e:
                sg.popup(f'Error: Something went wrong. {e}')
                continue
            window['-LOG-'].update('Generating plot...')
            window['-COL_PLOTS-'].update(visible=True)
            window['-IMAGE-']('')
            draw_figure(window['-IMAGE-'], procedure.figure)
            window['-LOG-'].update('DONE! Results and plots were saved in the given path')


if __name__ == '__main__':
    main()
