<<<<<<< HEAD
from cgitb import enable
from madap_cli import start_procedure
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasAgg
import PySimpleGUI as sg
import io
import time
=======
from posixpath import split
from tkinter import Scrollbar
import PySimpleGUI as sg
from madap_cli import start_procedure
>>>>>>> e1ec172 (More work on the GUI)
from madap.utils import gui_elements


class MadapGui:

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


<<<<<<< HEAD
def draw_figure(element, figure):
    """
    Draws the previously created "figure" in the supplied Image Element

    :param element: an Image Element
    :param figure: a Matplotlib figure
    :return: The figure canvas
    """

    plt.close('all')  # erases previously drawn plots
    canv = FigureCanvasAgg(figure)
    buf = io.BytesIO()
    canv.print_figure(buf, format='png')
    if buf is None:
        return None
    buf.seek(0)
    element.update(data=buf.read())
    return canv

def validate_fields(madap_gui):
    if madap_gui.file == '':
        sg.po('The data path is empty. Select a supported dataset file.', title='Input Error')
        return False
    if madap_gui.results == '':
        sg.popup_error('The result path is empty. Select a location for the results.', title='Input Error')
        return False
    if madap_gui.plots == []:
        sg.popup_error('Select the desired plot(s).', title='Input Error')
        return False
    if madap_gui.procedure == 'Impedance':
        if madap_gui.header_list and (len(madap_gui.header_list) not in [3,4]):
                sg.popup_error('Wrong number of header inputs.', title='Input Error')
                return False
        if madap_gui.specific and (len(madap_gui.specific) not in [3,4]):
                sg.popup_error('Wrong number of specific inputs.', title='Input Error')
                return False
    if madap_gui.procedure == 'Arrhenius':
        if madap_gui.header_list and (len(madap_gui.header_list) != 2):
                sg.popup_error('Wrong number of header inputs.', title='Input Error')
                return False
        if madap_gui.specific and (len(madap_gui.specific) != 2):
                sg.popup_error('Wrong number of specific inputs.', title='Input Error')
                return False

def gui_layout(madap, colors):
=======
def gui_layout(madap):
>>>>>>> e1ec172 (More work on the GUI)

    # ----------- Create a layout with 3 buttons for the different procedures ----------- #
    layout_buttons = [[ sg.Button("Impedance", key="-BUT_Impedance-", button_color=('white', 'black')),
                        sg.Button("Arrhenius", key="-BUT_Arrhenius-", button_color=colors),
                        sg.Button("Voltammetry", key="-BUT_Voltammetry-", button_color=colors)]]

    # ----------- Create a layout with a field for a data path and a result path ----------- #
    layout_data = [[sg.Text('Data Path', size=(10, 1)), sg.InputText(key='-DATA_PATH-', size=(55,1)), sg.FileBrowse(key='-BROWSE_DATA_PATH-')],
                   [sg.Text('Result Path', size=(10, 1)), sg.InputText(key='-RESULT_PATH-', size=(55,1)), sg.FolderBrowse(key='-BROWSE_RESULT_PATH-')],
                ]

    # ----------- Create a layout with a field for a data selection options ----------- #
    layout_data_selection = [[sg.Text('Headers or specific',justification='left', font=("Arial", 13))],
                             [sg.Combo(['Headers', 'Specific Region'], key='-HEADER_OR_SPECIFIC-', default_value='Headers')],
                             [sg.InputText(key='-HEADER_OR_SPECIFIC_VALUE-', tooltip=gui_elements.HEADER_OR_SPECIFIC_HELP, default_text="temp, cond")]]


    # ----------- Create tabs for Impedance procedure ----------- #
    tab_layout_EIS = [[sg.Text('This are the parameters for the EIS procedure')],
                    [sg.Text('Voltage (optional)',justification='left', font=("Arial", 13), pad=(1,(20,0)))],
                    [ sg.InputText(key="-voltage-", tooltip=gui_elements.VOLTAGE_HELP, enable_events=True), sg.Text('[V]')],
                    [sg.Text('Cell constant (optional)',justification='left', font=("Arial", 13), pad=(1,(20,0)))],
                    [sg.InputText(key="-cell_constant-", tooltip=gui_elements.CELL_CONSTANT_HELP, enable_events=True), sg.Text('[1/cm]')],
                    [sg.Text('Suggeted Circuit',justification='left', font=("Arial", 13), pad=(1,(20,0)))],
                    [sg.InputText(key="-suggested_circuit-", tooltip=gui_elements.SUGGESTED_CIRCUIT_HELP, default_text="R0-p(R1,CPE1)")],
                    [sg.Text('Initial Value', justification='left', font=("Arial", 13), pad=(1,(20,0)))],
                    [sg.InputText(key="-initial_value-", enable_events=True, tooltip=gui_elements.INITIAL_VALUES_HELP, default_text="[800,1e+14,1e-9,0.8]")],
                    [sg.Text('Plots',justification='left', font=("Arial", 13), pad=(1,(20,0)))],
                    [sg.Listbox([x for x in madap.eis_plots], key='-PLOTS_Impedance-', size=(50,len(madap.eis_plots)+1), select_mode=sg.SELECT_MODE_MULTIPLE, expand_x=True, expand_y=True)]]

    tab_layout_Liss = [[sg.Text('This is inside Lissajous')],
                [sg.Input(key='-inLiss-')]]

    tab_layout_Mott = [[sg.Text('This is inside Mottschosky')],
                    [sg.Input(key='-inMott-')]]

    # ----------- Layout the Impedance Options (Three TABS) ----------- #
    layout_Impedance = [[sg.TabGroup(
<<<<<<< HEAD
                        [[sg.Tab('EIS', tab_layout_EIS, key='-TAB_EIS-', expand_y=True),
                        sg.Tab('Lissajous', tab_layout_Liss,  background_color='darkred', key='-TAB_Lissajous-', expand_y=True),
                        sg.Tab('Mottschosky', tab_layout_Mott, background_color='darkgreen', key='-TAB_Mottschosky-', expand_y=True)]],
                        tab_location='topleft', selected_title_color='black', enable_events=True, expand_y=True)]]
=======
                        [[sg.Tab('EIS', tab_layout_EIS, key='-TAB_EIS-'),
                        sg.Tab('Lissajous', tab_layout_Liss,  background_color='darkred', key='-TAB_Lissajous-'),
                        sg.Tab('Mottschosky', tab_layout_Mott, background_color='darkgreen', key='-TAB_Mottschosky-')]],  tab_location='top', selected_title_color='black', enable_events=True)]]
>>>>>>> e1ec172 (More work on the GUI)

    # ----------- Layout the Arrhenius Options ----------- #
    layout_Arrhenius = [[sg.Text('This are the parameters for the Arrhenius procedure')],
                        [sg.Text('Plots',justification='left', font=("Arial", 13), pad=(1,(20,0)))],
                        [sg.Listbox([x for x in madap.arrhenius_plots], key='-PLOTS_Arrhenius-', size=(50,len(madap.arrhenius_plots)+1), select_mode=sg.SELECT_MODE_MULTIPLE, expand_x=True, expand_y=True)]]

    # ----------- TODO Layout the Voltammetry Options ----------- #
    layout_Voltammetry = [[sg.Text('This is Voltammetry')]]


    # ----------- Assemble the Procedure Column Element with the three layouts ----------- #
    procedure_column = [[sg.Column(layout_Impedance, key='-COL_Impedance-', scrollable=True, vertical_scroll_only=True, expand_x=True, expand_y=True),
                        sg.Column(layout_Arrhenius, visible=False, key='-COL_Arrhenius-', scrollable=True, vertical_scroll_only=True, expand_x=True, expand_y=True),
                        sg.Column(layout_Voltammetry, visible=False, key='-COL_Voltammetry-', scrollable=True, vertical_scroll_only=True, expand_x=True, expand_y=True)]]

    # ----------- Assemble the left Column Element ----------- #
    col1 = sg.Column([[sg.Frame('Data Selection:', layout_data_selection, font=("Arial", 15), size=(550, 120), expand_y=True)],
                      [sg.Frame('Methods:', procedure_column, font=("Arial", 15), size=(550, 500), expand_y=True)]],
                      expand_x=True, expand_y=True)

    # ----------- Layout the right Column Element ----------- #
    col2 = sg.Column([[sg.Frame('Plots:', [[sg.Image(key='-IMAGE-')]], visible=False, key='-COL_PLOTS-')]])

    # ----------- Assemble the main layout ----------- #
    layout = [
        [layout_buttons],
        [layout_data],
        [col1, col2],
        [sg.Text('',justification='left', font=("Arial", 13), pad=(1,(20,0)), key='-LOG-')],
        [sg.Button('RUN'), sg.Button('EXIT')]]

    return layout


def main():

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
        if event in ['-BUT_Impedance-', '-BUT_Arrhenius-', '-BUT_Voltammetry-']:
            event = event.strip('-BUT_')
            window[f'-COL_{madap_gui.procedure}-'].update(visible=False)
            window[f'-BUT_{madap_gui.procedure}-'].update(button_color=colors)
            window[f'-COL_{event}-'].update(visible=True)
            window[f'-BUT_{event}-'].update(button_color=('white', 'black'))
            madap_gui.procedure = event
        if values[0] in ['-TAB_EIS-', '-TAB_Lissajous-', '-TAB_Mottschotcky-']:
<<<<<<< HEAD
            madap_gui.impedance_procedure = values[0].strip('-TAB_')

        # Prevent the user from inoutting a value that is not a number in the voltage, cell constant and initial_value input field
=======
            # Create an "empty" class for the selected procedure every time the tab is shifted
            # This should prevent the user from changing the procedure without selecting a new tab
            madap_gui = MadapGui()
            madap_gui.impedance_procedure = values[event].strip('-TAB_')
>>>>>>> e1ec172 (More work on the GUI)
        if event == '-voltage-' and len(values['-voltage-']) and values['-voltage-'][-1] not in ('012345678890,.'):
            window['-voltage-'].update(values['-voltage-'][:-1])
        if event == '-cell_constant-' and len(values['-cell_constant-']) and values['-cell_constant-'][-1] not in ('012345678890,.'):
            window['-cell_constant-'].update(values['-cell_constant-'][:-1])
        if event == '-initial_value-' and len(values['-initial_value-']) and values['-initial_value-'][-1] not in ('012345678890,.e-+[]'):
            window['-initial_value-'].update(values['-initial_value-'][:-1])
        if event == 'RUN':
<<<<<<< HEAD
            window['-LOG-'].update('Starting procedure...')
            madap_gui.procedure
            madap_gui.file = values['-DATA_PATH-']
            madap_gui.results = values['-RESULT_PATH-']
            madap_gui.plots = values[f'-PLOTS_{madap_gui.procedure}-']
            madap_gui.voltage = values['-voltage-']
            madap_gui.cell_constant = values['-cell_constant-']
            madap_gui.suggested_circuit = values['-suggested_circuit-'] if not values['-suggested_circuit-'] == '' else None
            madap_gui.initial_values = values['-initial_value-'] if not values['-initial_value-'] == '' else None
=======
            madap_gui.procedure
            madap_gui.file = values['-DATA_PATH-']
            madap_gui.results = values['-RESULT_PATH-']
            madap_gui.plots = values['-EIS_PLOTS-']
            madap_gui.voltage = values['-voltage-']
            madap_gui.cell_constant = values['-cell_constant-']
            madap_gui.suggested_circuit = values['-suggested_circuit-']
            madap_gui.initial_value = list(values['-initial_value-'].split(","))
>>>>>>> e1ec172 (More work on the GUI)
            if values['-HEADER_OR_SPECIFIC-'] == 'Headers':
                madap_gui.header_list = values['-HEADER_OR_SPECIFIC_VALUE-'].replace(" ","")
                madap_gui.header_list = list(madap_gui.header_list.split(','))
            else:
                madap_gui.specific = values['-HEADER_OR_SPECIFIC_VALUE-'].replace(" ","")
                madap_gui.specific = list(madap_gui.specific.split(','))
<<<<<<< HEAD

            # Validate the fields
            validation = validate_fields(madap_gui)
            if validation == False:
                window['-LOG-'].update('Inputs were not valid! Try again.')
                continue
            try:
                procedure = start_procedure(madap_gui)
            except Exception as e:
                sg.popup(f'Error: Something went wrong.')
                continue
            window['-LOG-'].update('Generating plot...')
            window['-COL_PLOTS-'].update(visible=True)
            window['-IMAGE-']('')
            draw_figure(window['-IMAGE-'], procedure.figure)
            window['-LOG-'].update('DONE! Results and plots were saved in the given path')

=======
            print(madap_gui)
            start_procedure(madap_gui)
            window.close()
            break
    window.close()
>>>>>>> e1ec172 (More work on the GUI)

if __name__ == '__main__':
    main()