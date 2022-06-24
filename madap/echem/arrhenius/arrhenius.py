import os
from re import sub
from attrs import define, field
from attrs.setters import frozen
import numpy as np
import math
from utils import utils
from sklearn.linear_model import LinearRegression
from echem.procedure import EChemProcedure
from echem.arrhenius.arrhenius_plotting import ArrheniusPlotting as aplt
from madap import logger
import matplotlib.pyplot as plt

log = logger.get_logger("arrhenius")
@define
class Arrhenius(EChemProcedure):
    """
    Arrhenius class
    """
    temperatures: list[float] = field(on_setattr=frozen)
    conductivity: list[float] = field(on_setattr=frozen)
    gas_constant = 8.314        # [J/mol.K]
    activation = None           # [mJ/mol]
    arrhenius_constant = None   # [S.cm⁻¹]
    inverted_scale_temperatures = None
    fit_score = None
    ln_conductivity_fit = None
    intercept = None
    coefficients = None

    def analyze(self):
        # the linear fit formula: ln(sigma) = -E/RT + ln(A)
        self._cel_to_thousand_over_kelvin()

        reg = LinearRegression().fit(self.inverted_scale_temperatures.values.reshape(-1,1), self._log_conductivity())
        self.fit_score = reg.score(self.inverted_scale_temperatures.values.reshape(-1,1), self._log_conductivity())
        self.coefficients, self.intercept = reg.coef_[0], reg.intercept_
        self.arrhenius_constant = math.exp(reg.intercept_)
        self.activation = reg.coef_[0]*(-self.gas_constant)
        self.ln_conductivity_fit = reg.predict(self.inverted_scale_temperatures.values.reshape(-1,1))

        log.info(f"Arrhenius constant is {round(self.arrhenius_constant,4)}   [S.cm⁻¹] and activation is {round(self.activation,4)} [mJ/mol] with the score {self.fit_score}")


    def plot(self, save_dir:str, plots:list):
        plot_dir = utils.create_dir(os.path.join(save_dir, "plots"))
        plot = aplt()

        fig, available_axes = plot.compose_arrhenius_subplot(plots=plots)
        for sub_ax, plot_name in zip(available_axes, plots):
            if plot_name == "arrhenius":
                plot.arrhenius(subplot_ax=sub_ax, temperatures= self.temperatures,
                               log_conductivity= self._log_conductivity(),
                               inversted_scale_temperatures = self.inverted_scale_temperatures)
            elif plot_name == "arrhenius_fit":
                plot.arrhenius_fit(subplot_ax = sub_ax, temperatures = self.temperatures, log_conductivity = self._log_conductivity(),
                                inverted_scale_temperatures = self.inverted_scale_temperatures,
                                #intercept = self.intercept, slope = self.coefficients,
                                ln_conductivity_fit=self.ln_conductivity_fit, activation= self.activation,
                                arrhenius_constant = self.arrhenius_constant, r2_score= self.fit_score)
            else:
                log.error("Arrhenius class does not have the selected plot.")
        fig.tight_layout()

        name = utils.assemble_file_name(self.__class__.__name__)
        plot.save_plot(fig, plot_dir, name)

    def save_data(self, save_dir:str):
        """Save the results of the analysis.

        Args:
            save_dir (str): Directory where the data should be saved.
        """
        save_dir = utils.create_dir(os.path.join(save_dir, "data"))
        # Save the fitted circuit
        name = utils.assemble_file_name(self.__class__.__name__, "linear_fit.json")
        meta_data = {"R2_score": self.fit_score,'fit_slope': self.coefficients, "fit_intercept": self.intercept,
                    "arr_constant [S.cm⁻¹]": self.arrhenius_constant, "activation [mJ/mol]": self.activation,
                    "gas_constant [J/mol.K]": self.gas_constant}

        utils.save_data_as_json(directory=save_dir, name=name, data=meta_data)
        # Save the dataset
        data = utils.assemble_data_frame(**{"temperatures [\u00b0C]": self.temperatures,
                                            "conductivity [S\cm]": self.conductivity,
                                            "inverted_scale_temperatures [1000/K]": self.inverted_scale_temperatures,
                                            "log_conductivty [ln(S/cm)]": self._log_conductivity(),
                                            "log_conductivity_fit [ln(S/cm)]":self.ln_conductivity_fit})

        data_name = utils.assemble_file_name(self.__class__.__name__, "data.csv")
        utils.save_data_as_csv(save_dir, data, data_name)


    def perform_all_actions(self, save_dir:str, plots:list):
        self.analyze()
        self.plot(save_dir=save_dir, plots=plots)
        self.save_data(save_dir=save_dir)

    def _log_conductivity(self):
        return np.log(self.conductivity)

    def _cel_to_thousand_over_kelvin(self):
            converted_temps = 1000/(self.temperatures + 273.15)
            self.inverted_scale_temperatures = converted_temps
