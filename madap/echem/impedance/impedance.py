from dataclasses import dataclass, field
from impedance import preprocessing
from impedance.models.circuits import CustomCircuit, fitting
from impedance.validation import linKK
import numpy as np
import json
from echem.procedure import EChemProcedure
from madap import logger
from impedance_plotting import ImpedancePlotting as iplt

log = logger.get_logger("impedance")

# pylint: disable=unsubscriptable-object
@dataclass(frozen=True, order=True)
class EIS(EChemProcedure):
    frequency : list[float] = field(default_factory=list) #= format_data(data[freq_idx])
    real_impedance : list[float] = field(default_factory=list)
    imaginary_impedance : list[float] = field(default_factory=list)
    phase_shift : list[float] = field(default_factory=list)


    # Schönleber, M. et al. A Method for Improving the Robustness of linear Kramers-Kronig Validity Tests.
    # Electrochimica Acta 131, 20–27 (2014) doi: 10.1016/j.electacta.2014.01.034.
    def fit_eis(self, suggested_circuit: str = None, initial_value=None, max_rc_element: int=20, cut_off: float=0.85,
                fit_type: str='complex', val_low_freq=True, save_dir= None):
        f, Z = np.array(self.frequency), np.array(self.real_impedance + 1j*self.imaginary_impedance)

        num_rc, eval_fit , Z_linKK, res_real, res_imag = linKK(f, Z, c=cut_off, max_M=max_rc_element, fit_type=fit_type, add_cap=val_low_freq)
        chi_val = self.chi_calculation(res_imag, res_real)
        log.info(f"Chi value from lin_KK method is {chi_val}")

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
                    customCircuit = customCircuit_guess
                    Z_fit = Z_fit_guess

        else:
                customCircuit = CustomCircuit(initial_guess=initial_value, circuit=suggested_circuit)
                customCircuit.fit(f, Z)
                Z_fit = customCircuit.predict(f)
                rmse_error = fitting.rmse(Z, Z_fit)

        iplt.nyquist()

        if save_dir:
            # save the data
            # save the plot
            customCircuit.save(r"\Repositories\MADAP\test.json")

        return None

    def chi_calculation(self, res_imag, res_real):
        return np.sum(np.square(res_imag) + np.square(res_real))

    def rmse_plausibility(self, rmse_error):
        if not rmse_error < 100:
            log.warning(f"A validated circuit was not found with having a fit error of {rmse_error}")


    def analyse(self):
        pass
    def plot(self):
        pass


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
 