from attrs import define, field
from attrs.setters import frozen
from impedance import preprocessing
from impedance.models.circuits import CustomCircuit, fitting
from impedance.validation import linKK
import numpy as np
import json
import os
from utils import utils
from echem.procedure import EChemProcedure
from madap import logger
import matplotlib.pyplot as plt
from echem.impedance.impedance_plotting import ImpedancePlotting as iplt

# reference the impedance library
log = logger.get_logger("impedance")

# pylint: disable=unsubscriptable-object
@define
class Impedance:
    frequency : list[float] = field(on_setattr=frozen)
    real_impedance : list[float] = field(on_setattr=frozen)
    imaginary_impedance : list[float] = field( on_setattr=frozen)
    phase_shift : list[float] = field(on_setattr=frozen)



#class EIS(Impedance):
class EIS(EChemProcedure):
    def __init__(self, impedance, voltage: float = None, suggested_circuit: str = None, initial_value = None, max_rc_element: int = 20,
                cut_off: float = 0.85, fit_type: str = 'complex', val_low_freq: bool = True):
        self.impedance = impedance
        self.voltage = voltage
        self.suggested_circuit = suggested_circuit
        self.initial_value = initial_value
        self.max_rc_element = max_rc_element
        self.cut_off = cut_off
        self.fit_type = fit_type
        self.val_low_freq = val_low_freq

    # Schönleber, M. et al. A Method for Improving the Robustness of linear Kramers-Kronig Validity Tests.
    # Electrochimica Acta 131, 20–27 (2014) doi: 10.1016/j.electacta.2014.01.034.
    def analyze(self):
        f, Z = np.array(self.impedance.frequency), np.array(self.impedance.real_impedance + 1j*self.impedance.imaginary_impedance)

        self.num_rc_linKK, self.eval_fit_linKK , self.Z_linKK, self.res_real, self.res_imag = linKK(f, Z, c=self.cut_off, max_M=self.max_rc_element,
                                                                        fit_type=self.fit_type, add_cap=self.val_low_freq)
        self.chi_val = self._chi_calculation(self.res_imag, self.res_real)
        log.info(f"Chi value from lin_KK method is {self.chi_val}")

        if any(x < 0 for x in self.impedance.imaginary_impedance):
            f, Z = preprocessing.ignoreBelowX(f, Z)

        # if the user did not choose any circuit, some default suggestions will be applied.
        if (self.suggested_circuit and self.initial_value) is None:
            with open(os.path.join(utils.PATH,"suggested_circuits.json"), "r") as file:
                suggested_circuits = json.load(file)

            rmse_error = None
            for guess_circuit, guess_value in suggested_circuits.items():
                # apply some random guess
                customCircuit_guess = CustomCircuit(initial_guess=guess_value, circuit=guess_circuit)

                try:
                    customCircuit_guess.fit(f, Z)

                except RuntimeError as e:
                    log.error(e)
                    continue

                Z_fit_guess = customCircuit_guess.predict(f)
                rmse_guess = fitting.rmse(Z, Z_fit_guess)
                log.info(f"With the guessed circuit {guess_circuit} the RMSE error is {rmse_guess}")

                if rmse_error==None:
                    rmse_error = rmse_guess

                if rmse_guess < rmse_error:
                    rmse_error = rmse_guess
                    self.custom_circuit = customCircuit_guess
                    self.Z_fit = Z_fit_guess
                

        else:
                self.custom_circuit = CustomCircuit(initial_guess=self.initial_value, circuit=self.suggested_circuit)
                self.custom_circuit.fit(f, Z)
                self.Z_fit = self.custom_circuit.predict(f)
                rmse_error = fitting.rmse(Z, self.Z_fit)

    def plot(self, save_dir, plots):

        plot_dir = utils.create_dir(os.path.join(save_dir, "plots"))
        plot = iplt()
        if len(plots)%2==0:
            num_row = num_column = len(plots)/2
        else:
            num_row, num_column = 1, len(plots)

        fig, ax = plt.subplots(num_row, num_column, figsize=(4, 4), constrained_layout=True)

        for i, plot_name in enumerate(plots):
            if plot_name =="nyquist":
                # plot.nyquist(ax=ax, frequency=self.impedance.frequency, real_impedance=self.impedance.real_impedance, imaginary_impedance=self.impedance.imaginary_impedance,
                #             ax_sci_notation='both', scientific_limit=3, scientific_label_colorbar=False, legend_label=True,
                #             voltage=self.voltage, norm_color=True)
                plot.nyquist_fit(ax=ax, frequency=self.impedance.frequency, real_impedance=self.impedance.real_impedance,
                                 imaginary_impedance=self.impedance.imaginary_impedance, Z_fit=self.Z_fit, chi=self.chi_val,
                                 suggested_circuit=self.custom_circuit.circuit,
                                 ax_sci_notation="both", scientific_limit=3, scientific_label_colorbar=False, legend_label=True,
                                 voltage=self.voltage, norm_color=True)

                # plot.residual(ax=ax, frequency=self.frequency, res_real=self.res_real, res_imag=self.res_imag,
                #               log_scale='x')
        name = utils.assemble_file_name(self.__class__.__name__)
        plot.save_plot(fig, plot_dir, name)

    def save_data(self, save_dir:str):
        save_dir = utils.create_dir(os.path.join(save_dir, "data"))
        # Save the fitted circuit
        name = utils.assemble_file_name(self.__class__.__name__, "circuit.json")
        self.custom_circuit.save(os.path.join(save_dir, f"{name}"))
        
        added_data = {'rc_linKK': self.num_rc_linKK, "eval_fit_linKK": self.eval_fit_linKK}
        utils.append_to_save_data(directory=save_dir, added_data=added_data, name=name)
        # Save the dataset
        data = utils.assemble_data_frame(**{"frequency": self.impedance.frequency, "impedance": self.impedance.real_impedance + 1j*self.impedance.imaginary_impedance, 
                                        "fit_impedance": self.Z_fit, "residual_real":self.res_real, "residual_imag":self.res_imag, 
                                        "Z_linKK": self.Z_linKK})
        data_name = utils.assemble_file_name(self.__class__.__name__, "data.csv")
        utils.save_data_as_csv(save_dir, data, data_name)

    def perform_all_actions(self, save_dir:str, plots:list):
        self.analyze()
        self.plot(save_dir, plots)
        self.save_data(save_dir)

    def _chi_calculation(self, res_imag, res_real):
        return np.sum(np.square(res_imag) + np.square(res_real))

    def _rmse_plausibility(self, rmse_error):
        if not rmse_error < 100:
            log.warning(f"A validated circuit was not found with having a fit error of {rmse_error}")

class Mottschotcky(EIS):
    def __init__(self, impedance, suggested_circuit: str = None, initial_value=None, max_rc_element: int = 20, cut_off: float = 0.85, fit_type: str = 'complex', val_low_freq=True):
        super().__init__(impedance, suggested_circuit, initial_value, max_rc_element, cut_off, fit_type, val_low_freq)

    def mottschotcky_analysis(self): 
        EIS.analyze()
        r = self.suggested_circuit.R_value()
    # TODO

    
    # nyquist
    # fit nyquist
    # bode
    # mott v vs 1/cp_2

    def lissajous_analysis(self):pass
    # TODO
    # legend is the frequency
    # i vs t
    # v vs t
    # i vs E
