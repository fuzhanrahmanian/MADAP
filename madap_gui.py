from posixpath import split
from tkinter import Scrollbar
import PySimpleGUI as sg
from madap_cli import start_procedure
from madap.utils import gui_elements


class MadapGui:

    eis_plots = ["nyquist" ,"nyquist_fit", "residual", "bode"]

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


def gui_layout(madap):

    # ----------- Create a layout with 3 buttons for the different procedures ----------- #
    layout_buttons = [[ sg.Button("Impedance", key="-BUT_Impedance-", button_color=('white', 'black')),
                        sg.Button("Arrhenius", key="-BUT_Arrhenius-"),
                        sg.Button("Voltammetry", key="-BUT_Voltammetry-")]]

    # ----------- Create a layout with a field for a data path and a result path ----------- #
    layout_data = [[sg.Text('Data Path', size=(15, 1)), sg.InputText(key='-DATA_PATH-', size=(55,1)), sg.FileBrowse(key='-BROWSE_DATA_PATH-')],
                   [sg.Text('Result Path', size=(15, 1)), sg.InputText(key='-RESULT_PATH-', size=(55,1)), sg.FolderBrowse(key='-BROWSE_RESULT_PATH-')],
                ]

    layout_data_selection = [[sg.Text('Headers or specific',justification='left', font="bold", pad=(1,(40,0)))],
                             [sg.Text(gui_elements.HEADER_OR_SPECIFIC_HELP, justification='left')],
                             [sg.Combo(['Headers', 'Specific Region'], key='-HEADER_OR_SPECIFIC-', default_value='Headers', size=(15,1))],
                             sg.InputText(key='-HEADER_OR_SPECIFIC_VALUE-', size=(55,1))]


    # ----------- Create tabs for Impedance procedure ----------- #
    tab_layout_EIS = [[sg.Text('This are the settings for the EIS procedure', size = (80,1))],
                    [sg.Text('Plots',justification='left', font="bold",  pad=(1,(40,0))),],
                    [sg.Listbox([x for x in madap.eis_plots], key='-EIS_PLOTS-', size=(50,len(madap.eis_plots)), select_mode=sg.SELECT_MODE_MULTIPLE)],
                    [sg.Text('Voltage',justification='left', font="bold", pad=(1,(40,0))), ],
                    [sg.Text(gui_elements.VOLTAGE_HELP, justification='left'), sg.InputText(key="-voltage-", enable_events=True), sg.Text('[V]')],
                    [sg.Text('Cell constant',justification='left', font="bold", pad=(1,(40,0)))],
                    [sg.Text(gui_elements.CELL_CONSTANT_HELP, justification='left'), sg.InputText(key="-cell_constant-", enable_events=True), sg.Text('[1/cm]')],
                    [sg.Text('Suggeted Circuit',justification='left', font="bold", pad=(1,(40,0)))],
                    [sg.Text(gui_elements.SUGGESTED_CIRCUIT_HELP, justification='left')],
                    [sg.InputText(key="-suggested_circuit-", size = (80,1))],
                    [sg.Text('Initial Value', justification='left', font="bold", pad=(1,(40,0)))],
                    [sg.Text(gui_elements.INITIAL_VALUES_HELP, justification='left')],
                    [sg.InputText(key="-initial_value-", size = (80,1), enable_events=True)]]

    tab_layout_Liss = [[sg.Text('This is inside Lissajous')],
                [sg.Input(key='-inLiss-')]]

    tab_layout_Mott = [[sg.Text('This is inside Mottschosky')],
                    [sg.Input(key='-inMott-')]]

    layout_Impedance = [[sg.TabGroup(
                        [[sg.Tab('EIS', tab_layout_EIS, key='-TAB_EIS-'),
                        sg.Tab('Lissajous', tab_layout_Liss,  background_color='darkred', key='-TAB_Lissajous-'),
                        sg.Tab('Mottschosky', tab_layout_Mott, background_color='darkgreen', key='-TAB_Mottschosky-')]],  tab_location='top', selected_title_color='black', enable_events=True)]]

    layout_Arrhenius = [[sg.Text('This is Arrhenius')]]

    layout_Voltammetry = [[sg.Text('This is Voltammetry')]]


    layout = [
        [layout_buttons],
        [layout_data],
        [layout_data_selection],
        [sg.Column(layout_Impedance, key='-COL_Impedance-'),
        sg.Column(layout_Arrhenius, visible=False, key='-COL_Arrhenius-'),
        sg.Column(layout_Voltammetry, visible=False, key='-COL_Voltammetry-')],
        [sg.Button('RUN'), sg.Button('EXIT')]]

    return layout
# Event loop

def main():

    sg.theme("DarkBlue")
    madap_gui = MadapGui()
    layout = gui_layout(madap_gui)
    title = 'MADAP: Modular Automatic Data Analysis Platform'
    window = sg.Window(title, layout, size=(1200, 1200))

    colors = (sg.theme_text_color(), sg.theme_background_color())
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
            # Create an "empty" class for the selected procedure every time the tab is shifted
            # This should prevent the user from changing the procedure without selecting a new tab
            madap_gui = MadapGui()
            madap_gui.impedance_procedure = values[event].strip('-TAB_')
        if event == '-voltage-' and len(values['-voltage-']) and values['-voltage-'][-1] not in ('012345678890,.'):
            window['-voltage-'].update(values['-voltage-'][:-1])
        if event == '-cell_constant-' and len(values['-cell_constant-']) and values['-cell_constant-'][-1] not in ('012345678890,.'):
            window['-cell_constant-'].update(values['-cell_constant-'][:-1])
        if event == '-initial_value-' and len(values['-initial_value-']) and values['-initial_value-'][-1] not in ('012345678890,.e-+[]'):
            window['-initial_value-'].update(values['-initial_value-'][:-1])
        if event == 'RUN':
            madap_gui.procedure
            madap_gui.file = values['-DATA_PATH-']
            madap_gui.results = values['-RESULT_PATH-']
            madap_gui.plots = values['-EIS_PLOTS-']
            madap_gui.voltage = values['-voltage-']
            madap_gui.cell_constant = values['-cell_constant-']
            madap_gui.suggested_circuit = values['-suggested_circuit-']
            madap_gui.initial_value = list(values['-initial_value-'].split(","))
            if values['-HEADER_OR_SPECIFIC-'] == 'Headers':
                madap_gui.header_list = values['-HEADER_OR_SPECIFIC_VALUE-'].replace(" ","")
                madap_gui.header_list = list(madap_gui.header_list.split(','))
            else:
                madap_gui.specific = values['-HEADER_OR_SPECIFIC_VALUE-'].replace(" ","")
                madap_gui.specific = list(madap_gui.specific.split(','))
            print(madap_gui)
            start_procedure(madap_gui)
            window.close()
            break
    window.close()

if __name__ == '__main__':
    main()