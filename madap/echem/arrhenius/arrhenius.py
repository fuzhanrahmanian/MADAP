import os
from attrs import define, field
from attrs.setters import frozen
import numpy as np
from utils import utils
from echem.procedure import EChemProcedure
from echem.arrhenius.arrhenius_plotting import ArrheniusPlotting as aplt
import matplotlib.pyplot as plt



@define
class Arrhenius(EChemProcedure):
    """
    Arrhenius class
    """
    temperatures: list[float] = field(on_setattr=frozen)
    conductivity: list[float] = field(on_setattr=frozen)
    
    activation = None
    arrhenius_constant = None

    def analyze(self):
        pass    # TODO

    def plot(self, save_dir:str, plots:list):
        plot_dir = utils.create_dir(os.path.join(save_dir, "plots"))
        plot = aplt()
        # use compose_arrgenius_subplot to create a subplot for each plot
        fig, ax = plt.subplots(1, 1, figsize=(3, 3))
        # TODO arrplot and its fitting
        plot.arrhenius(ax, self.temperatures, self._log_conductivity())
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
