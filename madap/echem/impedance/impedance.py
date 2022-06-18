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

log = logger.get_logger("impedance")

# pylint: disable=unsubscriptable-object
@define
class EIS(EChemProcedure):
    frequency : list[float] = field(on_setattr=frozen)
    real_impedance : list[float] = field(on_setattr=frozen)
    imaginary_impedance : list[float] = field( on_setattr=frozen)
    phase_shift : list[float] = field(on_setattr=frozen)
    voltage : float = None
    chi_val: float = None
    Z_fit: list[float] = None
    custom_circuit: str = None
    # def __post_init__(self) -> None:
    #     self.chi_val = None
    #     self.Z_fit = None
    #     self.custom_circuit = None

    # Schönleber, M. et al. A Method for Improving the Robustness of linear Kramers-Kronig Validity Tests.
    # Electrochimica Acta 131, 20–27 (2014) doi: 10.1016/j.electacta.2014.01.034.
    def fit_eis(self, suggested_circuit: str = None, initial_value=None, max_rc_element: int=20, cut_off: float=0.85,
                fit_type: str='complex', val_low_freq=True, save_dir= None):
        f, Z = np.array(self.frequency), np.array(self.real_impedance + 1j*self.imaginary_impedance)

        num_rc, eval_fit , Z_linKK, res_real, res_imag = linKK(f, Z, c=cut_off, max_M=max_rc_element, fit_type=fit_type, add_cap=val_low_freq)
        self.chi_val = self.chi_calculation(res_imag, res_real)
        log.info(f"Chi value from lin_KK method is {self.chi_val}")

        if any(x < 0 for x in self.imaginary_impedance):
            f, Z = preprocessing.ignoreBelowX(f, Z)

        # if the user did not choose any circuit, some default suggestions will be applied.
        if (suggested_circuit and initial_value) is None:
            with open("utils/suggested_circuits.json", "r") as file:
                suggested_circuits = json.load(file)

            # Random default threshold for rmse
            rmse_error = 100
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

                if rmse_guess < rmse_error:
                    rmse_error = rmse_guess
                    self.custom_circuit = customCircuit_guess
                    self.Z_fit = Z_fit_guess

        else:
                self.custom_circuit = CustomCircuit(initial_guess=initial_value, circuit=suggested_circuit)
                self.custom_circuit.fit(f, Z)
                self.Z_fit = self.custom_circuit.predict(f)
                rmse_error = fitting.rmse(Z, self.Z_fit)

        if save_dir:
            # save the data

            # save the fitted circuit
            self.custom_circuit.save(r"\Repositories\MADAP\test.json")

    def chi_calculation(self, res_imag, res_real):
        return np.sum(np.square(res_imag) + np.square(res_real))

    def rmse_plausibility(self, rmse_error):
        if not rmse_error < 100:
            log.warning(f"A validated circuit was not found with having a fit error of {rmse_error}")


    def analyse(self):
        pass
    

    def plot(self, save_dir, plot_names):

        plot_dir=utils.create_dir(os.path.join(save_dir, "plots"))
        plot = iplt()
        if len(plot_names)%2==0:
            num_row = num_column = len(plot_names)/2
        else:
            num_row, num_column = 1, len(plot_names)

        fig, ax = plt.subplots(num_row, num_column, figsize=(4, 4), constrained_layout=True)

        for i, plot_name in enumerate(plot_names):
            if plot_name =="nyquist":
                #plot.nyquist(ax=ax, frequency=self.frequency, real_impedance=self.real_impedance, imaginary_impedance=self.imaginary_impedance,
                #             legend_label=True, voltage=self.voltage)
                plot.nyquist_fit(ax=ax, frequency=self.frequency, real_impedance=self.real_impedance,
                                 imaginary_impedance=self.imaginary_impedance, Z_fit=self.Z_fit, chi=self.chi_val,
                                 suggested_circuit=self.custom_circuit.circuit,
                                 legend_label=True, voltage=self.voltage)
            #iplt.bode(ax[0:1], plot_dir)
            #iplt.nyquist_fit(ax[1:0], plot_dir)
            #iplt.residual(ax[1:1], plot_dir)
        #plt.show()
        plot.save_plot(fig, plot_dir, self.__class__.__name__)


# class EIS_A(plot, data): # plot and data of our defined classes maybe open a folder calls "util" and we can call it from there.
# There data will be assembled, new directories can be created, dataframe can be built.
#                        # from plot we will import the plot styles, colots, type, subplots, colot bar , legend ... maybe learn the kwargs**

#         # logging info to show the what we gave
#         def nyquist_plot():pass
#         def bode_plot(): pass
#         def fit_eis(): pass # with randles, custom or used the predefined one, give the equivalent circuit and its paramteres (optinional save or not)
#         def prediifined_circuits(): pass # maybe push this somewhere else , in something like config or so
#         def plot_real_measured(): pass # draw fitted versus real in byquist plot and draw the circuit on the side
#         def validity_fit():pass # get the residuals, chi square of real , imaginary and both # show consistency and over/under fit
#         def plot_residual(): pass # should be part of validity
#         def llissajous_plot(): pass # show the linearity V-I , v vs time and i vs time , stability , and casuality and stability
#         def analsys_eis(): pass # all the functionions except lissajous
 
