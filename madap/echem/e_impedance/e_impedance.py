"""Impedance Analysis module."""
import os
import json
import numpy as np
import warnings
from attrs import define, field
from attrs.setters import frozen

import impedance.validation as validation
import impedance.preprocessing as preprocessing
import impedance.models.circuits as circuits
from madap.utils import utils
from madap.data_acquisition import data_acquisition as da
from madap import logger
from madap.echem.procedure import EChemProcedure
from madap.echem.e_impedance.e_impedance_plotting import ImpedancePlotting as iplt

warnings.warn("deprecated", DeprecationWarning)
# reference the impedance library
log = logger.get_logger("impedance")

# pylint: disable=unsubscriptable-object
@define
class EImpedance:
    """Class for data definition that will be used during the Impedance analysis.
        The data includes the following: frequency, real impedance, imaginary impedance,
        and the phase shift. These attributes are all pandas.Series. and will stay immutable except the phase shift.
    """
    frequency : list[float] = field(on_setattr=frozen)
    real_impedance : list[float] = field(on_setattr=frozen)
    imaginary_impedance : list[float] = field( on_setattr=frozen)
    phase_shift : list[float] = field(default=None)

    def __repr__(self) -> str:
        """Returns a string representation of the object."""
        return f"Impedance(frequency={self.frequency}, real_impedance={self.real_impedance}, \
                imaginary_impedance={self.imaginary_impedance}, phase_shift={self.phase_shift})"

    # def __post_init__(self):
    #     """Initialize the object."""
    #     self.phase_shift = self.calculate_phase_shift() if self.phase_shift is None else self.phase_shift

    # def __call__(self):
    #     if self.phase_shift is None:
    #         self.phase_shift = self.calculate_phase_shift()

class EIS(EChemProcedure):
    """General EIS class for the analysis of the EIS data.

    Args:
        EChemProcedure (cls): Parent abstract class
    """
    def __init__(self, impedance, voltage: float = None, suggested_circuit: str = None,
                initial_value = None, max_rc_element: int = 50,
                cut_off: float = 0.85, fit_type: str = 'complex',
                val_low_freq: bool = True, cell_constant="n"):
        """ Initialize the EIS class.

        Args:
            impedance (np.array): Impedance data containing real and imaginary part.
            voltage (float, optional): Voltage of the EIS measurement. Defaults to None.
            suggested_circuit (str, optional): String defining the suggested circuit. Defaults to None.
            initial_value (list, optional): Initial value of the circuit's element. Defaults to None.
            max_rc_element (int, optional): Maximum number of RC element to be used in the circuit. Defaults to 50.
            cut_off (float, optional): Cut off value of the fitted elements. Defaults to 0.85.
            fit_type (str, optional): Fit type. Defaults to 'complex'.
            val_low_freq (bool, optional): If True, the low frequency is used for the fit. Defaults to True.
            cell_constant (str, optional): Cell constant. Defaults to "n".
        """
        self.impedance = impedance
        self.voltage = voltage
        self.suggested_circuit = suggested_circuit
        self.initial_value = initial_value
        self.max_rc_element = max_rc_element
        self.cut_off = cut_off
        self.fit_type = fit_type
        self.val_low_freq = val_low_freq
        self.cell_constant = cell_constant
        self.conductivity = None
        self.rmse_calc = None
        self.num_rc_linkk = None
        self.eval_fit_linkk = None
        self.z_linkk = None
        self.res_real = None
        self.res_imag = None
        self.chi_val = None
        self.custom_circuit = None
        self.z_fit = None
        self.impedance.phase_shift = self._calculate_phase_shift() if self.impedance.phase_shift is None else self.impedance.phase_shift
        self.figure = None


    # Schönleber, M. et al. A Method for Improving the Robustness of
    # linear Kramers-Kronig Validity Tests.
    # Electrochimica Acta 131, 20–27 (2014) doi: 10.1016/j.electacta.2014.01.034.
    def analyze(self):
        """General function for performing the impedance analysis.
        This will fit the circuit and calculate the conductivity if is applicable.
        """
        f_circuit, z_circuit = np.array(self.impedance.frequency), np.array(self.impedance.real_impedance +
               1j*self.impedance.imaginary_impedance)

        self.num_rc_linkk, self.eval_fit_linkk , self.z_linkk, self.res_real, self.res_imag = validation.linKK(f_circuit, z_circuit, c=self.cut_off, max_M=self.max_rc_element,
                                                                        fit_type=self.fit_type, add_cap=self.val_low_freq)
        self.chi_val = self._chi_calculation()
        log.info(f"Chi value from lin_KK method is {self.chi_val}")

        if any(x < 0 for x in self.impedance.imaginary_impedance):
            f_circuit, z_circuit = preprocessing.ignoreBelowX(f_circuit, z_circuit)

        # if the user did not choose any circuit, some default suggestions will be applied.
        if (self.suggested_circuit and self.initial_value) is None:
            with open(os.path.join("madap", "utils", "suggested_circuits.json"), "r") as file:
                suggested_circuits = json.load(file)

            for guess_circuit, guess_value in suggested_circuits.items():
                # apply some random guess
                custom_circuit_guess = circuits.CustomCircuit(initial_guess=guess_value, circuit=guess_circuit)

                try:
                    custom_circuit_guess.fit(f_circuit, z_circuit)

                except RuntimeError as exp:
                    log.error(exp)
                    continue

                z_fit_guess = custom_circuit_guess.predict(f_circuit)
                rmse_guess = circuits.fitting.rmse(z_circuit, z_fit_guess)
                log.info(f"With the guessed circuit {guess_circuit} the RMSE error is {rmse_guess}")

                if self.rmse_calc is None:
                    self.rmse_calc = rmse_guess

                if rmse_guess <= self.rmse_calc:
                    self.rmse_calc = rmse_guess
                    self.custom_circuit = custom_circuit_guess
                    self.z_fit = z_fit_guess
        else:
            self.custom_circuit = circuits.CustomCircuit(initial_guess=self.initial_value, circuit=self.suggested_circuit)
            self.custom_circuit.fit(f_circuit, z_circuit)
            self.z_fit = self.custom_circuit.predict(f_circuit)
            self.rmse_calc = circuits.fitting.rmse(z_circuit, self.z_fit)
            log.info(f"With the guessed circuit {self.suggested_circuit} the RMSE error is {self.rmse_calc}")

        if self.cell_constant:
            # calculate the ionic conductivity if cell constant is available
            self.conductivity = self._conductivity_calculation()


    def plot(self, save_dir, plots, optional_name: str = None):
        """Plot the results of the analysis.

        Args:
            save_dir (str): directory where to save the data
            plots (list): list of plot types to be plotted
            optional_name (str, optional): name of the file to be saved. Defaults to None.
        """
        plot_dir = utils.create_dir(os.path.join(save_dir, "plots"))
        plot = iplt()
        fig, available_axes = plot.compose_eis_subplot(plots=plots)

        for sub_ax, plot_name in zip(available_axes, plots):
            if plot_name =="nyquist":
                sub_ax = available_axes[0] if ((len(plots)==4) or (len(plots)==3)) else sub_ax

                plot.nyquist(subplot_ax=sub_ax, frequency=self.impedance.frequency, real_impedance=self.impedance.real_impedance,
                            imaginary_impedance=self.impedance.imaginary_impedance,
                            ax_sci_notation='both', scientific_limit=3, scientific_label_colorbar=False, legend_label=True,
                            voltage=self.voltage, norm_color=True)

            elif plot_name == "nyquist_fit":
                sub_ax = available_axes[2] if len(plots)==4 else \
                        (available_axes[0] if (len(plots)==3 and (("residual" in plots) and ("bode" in plots))) else \
                        (available_axes[1] if (len(plots)==3 and (("residual" in plots) or ("bode" in plots))) else sub_ax))

                plot.nyquist_fit(subplot_ax=sub_ax, frequency=self.impedance.frequency, real_impedance=self.impedance.real_impedance,
                                 imaginary_impedance=self.impedance.imaginary_impedance, fitted_impedance=self.z_fit, chi=self.chi_val,
                                 suggested_circuit=self.custom_circuit.circuit,
                                 ax_sci_notation="both", scientific_limit=3, scientific_label_colorbar=False, legend_label=True,
                                 voltage=self.voltage, norm_color=True)

            elif plot_name == "bode":
                sub_ax = available_axes[1] if len(plots)==4 else (available_axes[1] if (len(plots)==3 and ("residual" in plots)) else
                                                                  (available_axes[2] if (len(plots)==3 and (not "residual" in plots)) else sub_ax))
                plot.bode(subplot_ax=sub_ax, frequency=self.impedance.frequency, real_impedance=self.impedance.real_impedance,
                          imaginary_impedance=self.impedance.imaginary_impedance,
                          phase_shift=self.impedance.phase_shift, ax_sci_notation="y", scientific_limit=3, log_scale="x")

            elif plot_name == "residual":
                sub_ax = available_axes[3] if len(plots)==4 else (available_axes[2] if len(plots)==3 else sub_ax)
                plot.residual(subplot_ax=sub_ax, frequency=self.impedance.frequency, res_real=self.res_real,
                              res_imag=self.res_imag, log_scale='x')

            else:
                log.error("EIS class does not have the selected plot.")
                continue

        fig.tight_layout()
        self.figure = fig
        name = utils.assemble_file_name(optional_name, self.__class__.__name__) if \
                    optional_name else utils.assemble_file_name(self.__class__.__name__)

        plot.save_plot(fig, plot_dir, name)

    def save_data(self, save_dir:str, optional_name:str = None):
        """Save the results of the analysis.

        Args:
            save_dir (str): Directory where the data should be saved.
            optional_name (None): Optional name for the data.
        """
        save_dir = utils.create_dir(os.path.join(save_dir, "data"))
        # Save the fitted circuit
        name = utils.assemble_file_name(optional_name, self.__class__.__name__, "circuit.json") if \
        optional_name else utils.assemble_file_name(self.__class__.__name__, "circuit.json")

        self.custom_circuit.save(os.path.join(save_dir, f"{name}"))
        added_data = {'rc_linKK': self.num_rc_linkk, "eval_fit_linKK": self.eval_fit_linkk, "RMSE_fit_error": self.rmse_calc,
                      "conductivity [S/cm]": self.conductivity}
        utils.append_to_save_data(directory=save_dir, added_data=added_data, name=name)
        # Save the dataset
        data = utils.assemble_data_frame(**{"frequency [Hz]": self.impedance.frequency,
                                            "impedance [\u03a9]": self.impedance.real_impedance + 1j*self.impedance.imaginary_impedance,
                                            "fit_impedance [\u03a9]": self.z_fit, "residual_real":self.res_real, "residual_imag":self.res_imag,
                                            "Z_linKK [\u03a9]": self.z_linkk})
        data_name = utils.assemble_file_name(optional_name, self.__class__.__name__, "data.csv") if \
                        optional_name else  utils.assemble_file_name(self.__class__.__name__, "data.csv")

        utils.save_data_as_csv(save_dir, data, data_name)

    def perform_all_actions(self, save_dir:str, plots:list, optional_name:str = None):
        """ Wrapper function for executing all action

        Args:
            save_dir (str): Directory where the data should be saved.
            plots (list): List of plot types to be plotted.
        """
        self.analyze()
        self.plot(save_dir, plots, optional_name=optional_name)
        self.save_data(save_dir=save_dir, optional_name=optional_name)

    @property
    def figure(self):
        return self._figure

    @figure.setter
    def figure(self, figure):
        self._figure = figure

    def _chi_calculation(self):
        """ Calculate the chi value of the fit.

        Returns:
            float: chi value of the fit
        """
        return np.sum(np.square(self.res_imag) + np.square(self.res_real))

    def _conductivity_calculation(self):
        """ Calculate the conductivity of the circuit.

        Returns:
            float: conductivity of the circuit
        """
        conductivity = self.cell_constant * (1/self.custom_circuit.parameters_[0])
        log.info(f"The calculated conductivity is {conductivity} [S.cm⁻¹]")
        return conductivity

    def _calculate_phase_shift(self) -> list[float]:
        """calculate phase shift

        Args:
            imaginary_impedance (class): imaginary impedance data
            real_impedance (class): real impedance data

        Returns:
            phase shift: calculated phase shift based on real and imaginary data
        """

        phase_shift_in_rad = np.arctan(da.format_data(
                             abs(-self.impedance.imaginary_impedance)/da.format_data(abs(self.impedance.real_impedance))))
        return np.rad2deg(phase_shift_in_rad)


class Mottschotcky(EIS, EChemProcedure):
    """ Class for performing the Mottschotcky procedure.

    Args:
        EIS (class): General EIS class
        EChemProcedure (class): General abstract EChem Procedure class
    """
    def __init__(self, impedance, suggested_circuit: str = None, initial_value=None,
                 max_rc_element: int = 20, cut_off: float = 0.85, fit_type: str = 'complex', val_low_freq=True):
        EIS().__init__(impedance, suggested_circuit, initial_value, max_rc_element, cut_off, fit_type, val_low_freq)

    def analysis(self):
        EIS.analyze()

    def plot(self, save_dir, plots): pass
    # TODO
    # nyquist
    # fit nyquist
    # bode
    # mott v vs 1/cp_2
    def save_data(self, save_dir: str):pass

    def perform_all_actions(self, save_dir: str, plots: list):pass

class Lissajous(EChemProcedure):
    def __init__(self) -> None:
        pass
    def analyze():
        pass

    def plot():
        pass
    # TODO
    # legend is the frequency
    # i vs t
    # v vs t
    # i vs E
    def save_data():
        pass
    def perform_all_actions():
        pass
