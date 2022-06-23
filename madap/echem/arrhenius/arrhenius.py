import os
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
    gas_constant = 8.314  # J/mol.K
    activation = None     # mJ/mol
    arrhenius_constant = None
    inverted_scale_temperatures = None
    fit_score = None
    ln_conductivity_fit = None

    def analyze(self):
        # the linear fit formula: ln(sigma) = -E/RT + ln(A)
        self._cel_to_thousand_over_kelvin()

        reg = LinearRegression().fit(self.inverted_scale_temperatures.values.reshape(-1,1), self._log_conductivity())
        self.fit_score = reg.score(self.inverted_scale_temperatures.values.reshape(-1,1), self._log_conductivity())
        self.arrhenius_constant = math.exp(reg.intercept_)
        self.activation = reg.coef_[0]*(-self.gas_constant)
        self.ln_conductivity_fit = reg.predict(self.inverted_scale_temperatures.values.reshape(-1,1))

        log.info(f"Arrhenius constant is {round(self.arrhenius_constant,4)} [ln(S.cm⁻¹] and activation is {round(self.activation,4)} [mJ/mol] with the score {self.fit_score}")


    def plot(self, save_dir:str, plots:list):
        plot_dir = utils.create_dir(os.path.join(save_dir, "plots"))
        plot = aplt()
        # use compose_arrgenius_subplot to create a subplot for each plot
        fig, ax = plt.subplots(1, 1, figsize=(3, 3))
        # TODO arrplot and its fitting
        plot.arrhenius(ax, self.temperatures, self._log_conductivity(), self.inverted_scale_temperatures)
        fig.tight_layout()

        name = utils.assemble_file_name(self.__class__.__name__)
        plot.save_plot(fig, plot_dir, name)

    def save_data(self, save_dir:str):
        pass    # TODO

    def perform_all_actions(self, save_dir:str, plots:list):
        self.analyze()
        self.plot(save_dir=save_dir, plots=plots)
        #self.save_data(save_dir=save_dir)
    def _log_conductivity(self):
        return np.log(self.conductivity)

    def _cel_to_thousand_over_kelvin(self):
            converted_temps = 1000/(self.temperatures + 273.15)
            self.inverted_scale_temperatures = converted_temps
