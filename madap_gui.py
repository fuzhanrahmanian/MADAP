"""This module implements the GUI application for MADAP """
import io
import queue
import threading

import PySimpleGUI as sg

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasAgg

from madap.logger.logger import log_queue
from madap.utils import gui_elements
from madap_cli import start_procedure
class MadapGui:
    # pylint: disable=too-many-instance-attributes
    """This class implements the GUI application for MADAP
    """
    eis_plots = ["nyquist" ,"nyquist_fit", "residual", "bode"]
    arrhenius_plots = ["arrhenius", "arrhenius_fit"]
    ca_plots = ["CA", "Log_CA", "CC", "Cottrell", "Anson", "Voltage"]
    cp_plots = ["CP", "CC", "Cottrell", "Voltage_Profile", "Potential_Rate", "Differential_Capacity"]
    cv_plots = ["E-t", "I-t", "Peak-Scan", "CV", "Tafel"]

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
        self.voltammetry_procedure = None
        self.applied_current = None
        self.measured_current_units = None
        self.measured_time_units = None
        self.applied_voltage = None
        self.mass_of_active_material = None
        self.electrode_area = None
        self.concentration_of_active_material = None
        self.number_of_electrons = None
        self.window_size = None
        self.cycle_list = None
        self.penalty_value = None
        self.temperature = None
        self.applied_scan_rate = None

    # pylint: disable=inconsistent-return-statements
    # pylint: disable=too-many-return-statements
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
        # Check if the str of numbers of electrons is a number whole number
        if self.number_of_electrons and not self.number_of_electrons.isdigit():
            sg.popup_error('Number of electrons must be a number.', title='Input Error')
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
    layout_buttons = [[ sg.Button("Impedance", key="-BUT_Impedance-", button_color=('#F23D91', 'black'), font=("Arial", 14, "bold")),
                        sg.Button("Arrhenius", key="-BUT_Arrhenius-", button_color=colors, font=("Arial", 14, "bold")),
                        sg.Button("Voltammetry", key="-BUT_Voltammetry-", button_color=colors, font=("Arial", 14, "bold"))]]

    # ----------- Create a layout with a field for a data path and a result path ----------- #
    layout_data = [[sg.Text('Data Path', size=(10, 1)), sg.InputText(key='-DATA_PATH-',
                                                                     size=(55,1),
                                                                     default_text="path/to/data"),
                    sg.FileBrowse(key='-BROWSE_DATA_PATH-')],
                   [sg.Text('Result Path', size=(10, 1)), sg.InputText(key='-RESULT_PATH-',
                                                                       size=(55,1),
                                                                       default_text="path/to/results"),
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
    tab_layout_eis = [[sg.Text('This are the parameters for the EIS procedure', font=("Arial", 11))],
                    [sg.Text('Voltage (optional)',justification='left', font=("Arial", 11),pad=(1,(10,0))),
                    sg.InputText(key="-voltage-", tooltip=gui_elements.VOLTAGE_HELP,
                                 enable_events=True, size=(10,1), pad=((97,0), (10,0))), sg.Text('[V]', pad=((7,0),(10,0)))],

                    [sg.Text('Cell constant (optional)',justification='left', font=("Arial", 11),pad=(1,(10,0))),
                     sg.InputText(key="-cell_constant-", tooltip=gui_elements.CELL_CONSTANT_HELP,
                                  enable_events=True, size=(10,1), pad=((60,0), (10,0))), sg.Text('[1/cm]', pad=((7,0),(10,0)))],
                    [sg.Text("Upper limit of quantile (optional)",justification='left',
                             font=("Arial", 11), pad=(1,(10,0))),
                     sg.InputText(key="-upper_limit_quantile-", tooltip=gui_elements.UPPER_LIMIT_QUANTILE_HELP,
                                  enable_events=True, default_text="0.99",  size=(10,1), pad=((5,0), (10,0)))],
                    [sg.Text("Lower limit of quantile (optional)",justification='left',
                             font=("Arial", 11), pad=(1,(10,0))),
                    sg.InputText(key="-lower_limit_quantile-", tooltip=gui_elements.LOWER_LIMIT_QUANTILE_HELP,
                                  enable_events=True, default_text="0.01", size=(10,1), pad=((5,0), (10,0)))],
                    [sg.Text('Suggested Circuit',justification='left', font=("Arial", 11),
                             pad=(1,(10,0))),
                     sg.InputText(key="-suggested_circuit-", tooltip=gui_elements.SUGGESTED_CIRCUIT_HELP,
                                  default_text="R0-p(R1,CPE1)", size=(25,1), pad=((93,0), (10,0)))],
                    [sg.Text('Initial Value', justification='left', font=("Arial", 11), pad=(1,(10,0))),
                     sg.InputText(key="-initial_value-", enable_events=True, tooltip=gui_elements.INITIAL_VALUES_HELP,
                                  default_text="[860, 3e+5, 1e-09, 0.90]", size=(25,1), pad=((137,0), (10,0)))],
                    [sg.Text('Plots',justification='left', font=("Arial", 11), pad=(1,(10,0)))],
                    [sg.Listbox([x for x in madap.eis_plots], key='-PLOTS_Impedance-',
                                size=(33,len(madap.eis_plots)), select_mode=sg.SELECT_MODE_MULTIPLE,
                                expand_x=True, expand_y=True)]]

    tab_layout_liss = [[sg.Text('WORK IN PROGRESS: Lissajous')],
                [sg.Input(key='-inLiss-')]]

    tab_layout_mott = [[sg.Text('WORK IN PROGRESS: Mottschosky')],
                    [sg.Input(key='-inMott-')]]

    # ----------- Create tabs for Voltammetry procedure ----------- #
    tab_layout_ca = [
                    [sg.Text('Applied Voltage (optional)',justification='left', font=("Arial", 11), pad=(1,(15,0))),
                     sg.InputText(key='-inCAVoltage-', default_text="0.43", tooltip=gui_elements.VOLTAGE_HELP, size=(10, 1),
                                  pad=((5,0),(10,0))), sg.Text('[V]', pad=((7,0),(10,0)))],
                    [sg.Text('Window size (optional)',justification='left', font=("Arial", 11), pad=(1,(10,0))),
                     sg.InputText(key='-inVoltWindowSize-', default_text="20000", tooltip=gui_elements.WINDOW_SIZE_HELP, size=(10, 1),
                                  pad=((20,0),(10,0)))],
                    [sg.Text('Plots',justification='left', font=("Arial", 11), pad=(1,(10,0)))],
                    [sg.Listbox([x for x in madap.ca_plots], key='-PLOTS_CA-',
                                size=(33,len(madap.ca_plots)), select_mode=sg.SELECT_MODE_MULTIPLE,
                                expand_x=False, expand_y=False)]]
    tab_layout_cp = [[sg.Text('Applied Current (optional)',justification='left', font=("Arial", 11), pad=(1,(15,0))),
                      sg.InputText(key='-inCPCurrent-',  default_text="0.000005", tooltip=gui_elements.APPLIED_CURRENT_HELP, size=(10, 1),
                                   pad=((5,0),(10,0))), sg.Text('[A]', pad=((7,0),(10,0)))],
                    [sg.Text('Penalty value (optional)',justification='left', font=("Arial", 11), pad=(1,(10,0))),
                    sg.InputText(key='-inPenaltyValue-', default_text="0.25", tooltip=gui_elements.PENALTY_VALUE_HELP, size=(10, 1),
                                 pad=((20,1), (10,0)))],
                    [sg.Text('Plots',justification='left', font=("Arial", 11), pad=(1,(10,0)))],
                    [sg.Listbox([x for x in madap.cp_plots], key='-PLOTS_CP-',
                                size=(33,len(madap.cp_plots)), select_mode=sg.SELECT_MODE_MULTIPLE,
                                expand_x=False, expand_y=False)]]
    tab_layout_cv = [[sg.Text('Plotted Cycle(s) (optional)',justification='left', font=("Arial", 11), pad=(1,(15,0))),
                      sg.InputText(key='-inPlotCycleList-', default_text="1", tooltip=gui_elements.WINDOW_SIZE_HELP, size=(10, 1),
                                   pad=(1,(10,0)))],
                    [sg.Text('Temperature (optional)',justification='left', font=("Arial", 11), pad=(1,(10,0))),
                      sg.Input(key='-inCVTemperature-', default_text="298.15", size=(10, 1), pad=((20,0),(10,0))), sg.Text('[K]',
                                    pad=((7,0),(10,0)))],
                    [sg.Text('Applied Scan Rate (optional)',justification='left', font=("Arial", 11), pad=(1,(10,0))),
                        sg.Input(key='-inCVScanRate-', default_text="0.1", size=(10, 1), pad=((20,0),(10,0))), sg.Text('[V/s]',
                                    pad=((7,0),(10,0)))],
                    [sg.Text('Plots',justification='left', font=("Arial", 11), pad=(1,(10,0)))],
                    [sg.Listbox([x for x in madap.cv_plots], key='-PLOTS_CV-',
                                size=(33,len(madap.cv_plots)), select_mode=sg.SELECT_MODE_MULTIPLE,
                                expand_x=False, expand_y=False)]]

    # ----------- Layout the Impedance Options (Three TABS) ----------- #
    layout_impedance = [[sg.TabGroup(
                        [[sg.Tab('EIS', tab_layout_eis, key='-TAB_EIS-', expand_y=True),
                        sg.Tab('Lissajous', tab_layout_liss,  background_color='darkred',
                               key='-TAB_Lissajous-', expand_y=True),
                        sg.Tab('Mottschosky', tab_layout_mott, background_color='darkgreen',
                               key='-TAB_Mottschosky-', expand_y=True)]],
                        tab_location='topleft', selected_title_color='#F23D91', tab_background_color = "#FF7F69",
                        enable_events=True, expand_y=True, font=("Arial", 12, "bold"), pad=(1,(5,0)))]]

    # ----------- Layout the Arrhenius Options ----------- #
    layout_arrhenius = [[sg.Text('Plots',justification='left', font=("Arial", 11), pad=(1,(20,0)))],
                        [sg.Listbox([x for x in madap.arrhenius_plots], key='-PLOTS_Arrhenius-',
                                    size=(33,len(madap.arrhenius_plots)+1),
                                    select_mode=sg.SELECT_MODE_MULTIPLE, expand_x=True,
                                    expand_y=True)]]

    # ----------- TODO Layout the Voltammetry Options ----------- #
    layout_voltammetry = [
                        [sg.Text('Measured Current Units', justification='left', font=("Arial", 11), pad=(1,(15,0))),
                        sg.Combo(['A', 'mA', 'uA'], key='-inVoltUnits-', default_value='A', enable_events=True, pad=(10,(15,0)),
                                 tooltip=gui_elements.MEASURED_CURRENT_UNITS_HELP, size=(5, 1))],

                        [sg.Text('Measured Time Units', justification='left', font=("Arial", 11), pad=(1,(15,0))),
                        sg.Combo(['h', 'min', 's', 'ms'], key='-inVoltTimeUnits-', default_value='s', enable_events=True, pad=(25,(15,0)),
                                 tooltip=gui_elements.MEASURED_TIME_UNITS_HELP, size=(5, 1))],

                        [sg.Text('Number of electrons n', justification='left', font=("Arial", 11), pad=(1,(15,0))),
                        sg.InputText(key='-inVoltNumberElectrons-', default_text="1", size=(5, 1), pad=(20,(15,0)))],

                        [sg.Text('Concentration of active material (optional)', justification='left', font=("Arial", 11),  pad=(1,(15,0))),
                        sg.InputText(key='-inVoltConcentration-', default_text="1", size=(5, 1), pad=(10,(15,0))),
                        sg.Text('[mol/cm3]', justification='left', font=("Arial", 11), pad=(1,(15,0)))],

                        [sg.Text('Mass of active material (optional)',justification='left', font=("Arial", 11), pad=(1,(15,0))),
                        sg.InputText(key='-inCAMass-', default_text="0.0001", size=(10, 1), pad=((65,5),(15,0))),
                        sg.Text('[g]', justification='left', font=("Arial", 11), pad=(1,(15,0)))],

                        [sg.Text('Electrode area (optional)',justification='left', font=("Arial", 11), pad=(1,(15,0))),
                        sg.InputText(key='-inCAArea-', default_text="0.196", size=(10, 1), pad=((120,5),(15,0))),
                        sg.Text('[cm2]', justification='left', font=("Arial", 11), pad=(1,(15,0)))],

                        [sg.TabGroup([[sg.Tab('Chrono-Potentiometry', tab_layout_cp, key='-TAB_CP-', expand_y=True),
                                    sg.Tab('Chrono-Amperomtery', tab_layout_ca, key='-TAB_CA-', expand_y=True),
                                    sg.Tab('Cyclic Voltammetry', tab_layout_cv, key='-TAB_CV-', expand_y=True)]],
                                    tab_location='topleft', selected_title_color='#F23D91', background_color='#282312',
                                    tab_background_color = "#FF7F69",
                                    enable_events=True, expand_y=True, font=("Arial", 12, "bold"), pad=(1,(40,0)))]
]



    # ----------- Assemble the Procedure Column Element with the three layouts ----------- #
    procedure_column = [[sg.Column(layout_impedance, key='-COL_Impedance-', scrollable=True,
                                   vertical_scroll_only=True, expand_x=True, expand_y=True),
                        sg.Column(layout_arrhenius, visible=False, key='-COL_Arrhenius-',
                                  scrollable=True, vertical_scroll_only=True, expand_x=True,
                                  expand_y=True),
                        sg.Column(layout_voltammetry, visible=False, key='-COL_Voltammetry-',
                                  scrollable=True, vertical_scroll_only=True, expand_x=True,
                                  expand_y=True)]]

    # ----------- Assemble the left Column Element ----------- #
    col1 = sg.Column([[sg.Frame('Data Selection:', layout_data_selection, font=("Arial", 15, "bold"),
                                size=(550, 120), expand_y=True)],
                      [sg.Frame('Methods:', procedure_column, font=("Arial", 15, "bold"), size=(550, 550),
                                expand_y=True)]],
                      expand_x=True, expand_y=True)

    # ----------- Layout the right Column Element ----------- #
    col2 = sg.Column([[sg.Frame('Plots:', [[sg.Image(key='-IMAGE-')]], visible=False, font=("Arial", 15, "bold"),
                                key='-COL_PLOTS-')]])

    # ----------- Assemble the main layout ----------- #
    layout = [
        [layout_buttons],
        [layout_data],
        [col1, col2],
        [sg.Text('',justification='left', font=("Arial", 13), pad=(1,(20,0)), key='-LOG-',
                 enable_events=True)],
        [sg.Button('RUN'), sg.Button('EXIT')],
        [sg.Multiline(size=(100, 5), key='LogOutput', autoscroll=True, background_color='black', text_color='#0CF2F2')],]

    return layout


def main():
    # pylint: disable=too-many-branches
    """Main function of the GUI
    """

    # Defining the custom theme 'MADAP' using the provided hex values
    sg.LOOK_AND_FEEL_TABLE['MADAP'] = {
        'BACKGROUND': '#0D0D0D',
        'TEXT': '#0CF2F2',
        'INPUT': '#E5B9AB',
        'TEXT_INPUT': '#2B2840',
        'SCROLL': '#2B2840',
        'BUTTON': ('white', '#2B2840'),
        'PROGRESS': ('#F27166', '#0D0D0D'),
        'BORDER': 1, 'SLIDER_DEPTH': 0, 'PROGRESS_DEPTH': 0,
    }

    # Select a theme
    sg.theme("MADAP")

    # Create class with initial values
    madap_gui = MadapGui()

    # Get primary colors and assemble window
    colors = (sg.theme_text_color(), sg.theme_background_color())
    layout = gui_layout(madap_gui, colors)
    title = 'MADAP: Modular Automatic Data Analysis Platform'
    window = sg.Window(title, layout, icon="logo.ico", resizable=True)
    # Shared variable for the return value and a flag to indicate completion
    procedure_result = [None]  # List to hold the return value
    procedure_complete = [False]  # Flag to indicate completion
    procedure_error = [None]
    # Initialization for log update
    log_update_counter = 0
    log_update_max = 30
    is_procedure_running = False

    def procedure_wrapper():
        try:
            procedure_result[0] = start_procedure(madap_gui)
        except ValueError as e:
            procedure_error[0] = e
        finally:
            procedure_complete[0] = True
    # Event loop
    while True:
        event, values = window.read(timeout=100)
        if event in (sg.WIN_CLOSED, 'EXIT'):
            break
        if event in ['-BUT_Impedance-', '-BUT_Arrhenius-', '-BUT_Voltammetry-']:
            if event == '-BUT_Voltammetry-':
                # empty HEADER_OR_SPECIFIC_VALUE
                window['-HEADER_OR_SPECIFIC_VALUE-']('current, voltage, time')
            event = event.strip('-BUT_')
            window[f'-COL_{madap_gui.procedure}-'].update(visible=False)
            window[f'-BUT_{madap_gui.procedure}-'].update(button_color=colors)
            window[f'-COL_{event}-'].update(visible=True)
            window[f'-BUT_{event}-'].update(button_color=('#F23D91', 'black'))
            madap_gui.procedure = event
        if values[0] in ['-TAB_EIS-', '-TAB_Lissajous-', '-TAB_Mottschotcky-']:
            madap_gui.impedance_procedure = values[0].strip('-TAB_')
        if values[1] in ['-TAB_CA-', '-TAB_CP-', '-TAB_CV-']:
            madap_gui.voltammetry_procedure = values[1].split('_')[1].strip("-")

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
            # TODO: this needs to be expanded for Voltammetry
            if madap_gui.procedure in ('Impedance', 'Arrhenius'):
                madap_gui.plots = values[f'-PLOTS_{madap_gui.procedure}-']
            if madap_gui.procedure == 'Voltammetry':
                madap_gui.plots = values[f'-PLOTS_{madap_gui.voltammetry_procedure}-']
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
            madap_gui.applied_current = values['-inCPCurrent-'] \
                                            if not values['-inCPCurrent-'] == '' else None
            madap_gui.measured_current_units = values['-inVoltUnits-']
            madap_gui.measured_time_units = values['-inVoltTimeUnits-']
            madap_gui.applied_voltage = values['-inCAVoltage-'] \
                                            if not values['-inCAVoltage-'] == '' else None
            madap_gui.mass_of_active_material = values['-inCAMass-'] \
                                            if not values['-inCAMass-'] == '' else None
            madap_gui.electrode_area = values['-inCAArea-'] \
                                            if not values['-inCAArea-'] == '' else None
            madap_gui.concentration_of_active_material = values['-inVoltConcentration-'] \
                                            if not values['-inVoltConcentration-'] == '' else None
            madap_gui.number_of_electrons = values['-inVoltNumberElectrons-'] \
                                            if not values['-inVoltNumberElectrons-'] == '' else None
            madap_gui.window_size = values['-inVoltWindowSize-'] \
                                            if not values['-inVoltWindowSize-'] == '' else None
            madap_gui.cycle_list = values['-inPlotCycleList-'] \
                                            if not values['-inPlotCycleList-'] == '' else None
            madap_gui.penalty_value = values['-inPenaltyValue-'] \
                                            if not values['-inPenaltyValue-'] == '' else None
            madap_gui.temperature = values['-inCVTemperature-'] \
                                            if not values['-inCVTemperature-'] == '' else None
            madap_gui.applied_scan_rate = values['-inCVScanRate-'] \
                                            if not values['-inCVScanRate-'] == '' else None
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
            window['LogOutput'].update('')
            window['RUN'].update(disabled=True)
            procedure_thread = threading.Thread(target=procedure_wrapper)
            procedure_thread.start()
            is_procedure_running = True
            log_update_counter = 0  # Reset the counter
        # Update log output while the procedure is running or GUI is active
        update_log_output(window)

        # Update log message periodically
        if is_procedure_running and not procedure_complete[0]:
            log_update_counter = (log_update_counter + 1) % log_update_max
            num_dots = (log_update_counter // 10) % 3 + 1  # Cycle the dots
            log_message = "Analysing" + "." * num_dots
            window['-LOG-'].update(log_message)

        # Check for completion or errors from the background process
        if procedure_complete[0]:
            # Reset the completion flag
            is_procedure_running = False
            procedure_complete[0] = False

            if procedure_error[0]:
                sg.popup(f'Error: Something went wrong. {procedure_error[0]}')
                procedure_error[0] = None
            else:
                procedure_return_value = procedure_result[0]
                window['-LOG-'].update('Generating plot...')
                window['-COL_PLOTS-'].update(visible=True)
                window['-IMAGE-']('')
                draw_figure(window['-IMAGE-'], procedure_return_value.figure)
                window['-LOG-'].update('DONE! Results and plots were saved in the given path')
            # Reset the completion flag and re-enable the RUN button
            #procedure_complete[0] = False
            window['RUN'].update(disabled=False)

def update_log_output(window):
    """Reads log messages from the queue and updates the GUI."""
    while not log_queue.empty():
        try:
            record = log_queue.get_nowait()
            if record:
                window['LogOutput'].update(record.msg + '\n', append=True)
        except queue.Empty:
            break

if __name__ == '__main__':
    main()
