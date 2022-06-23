from madap import logger
from matplotlib import pyplot as plt
from matplotlib.lines import Line2D
import matplotlib.colors as mcl
import numpy as np
from plotting import Plots
from utils import utils


log = logger.get_logger("arrhenius_plotting")

class ArrheniusPlotting(Plots):

    def arrhenius(self, subplot_ax, temperature, log_conductivity,
            ax_sci_notation = None, scientific_limit: int = 3):

        # log conductivity should have unit of S/cm
        log.info("Creating Arrhenius plot")
        subplot_ax2=subplot_ax.twiny()
        self.plot_identity(subplot_ax, xlabel=r"$\frac{1000}{T}$ $[K^{-1}]$",
                           ylabel=r"$\log$($\sigma$) [$S.cm^{-1}$]",
                           ax_sci_notation=ax_sci_notation,
                           scientific_limit=scientific_limit)
        subplot_ax2.scatter(temperature, log_conductivity, s=10, c="black", rasterized=True)
        self.plot_identity(subplot_ax2, xlabel="$T$ [\u00b0C]")
        self.set_xtick_for_two_axes(subplot_ax, subplot_ax2, utils.cel_to_thousand_over_kelvin(temperature), temperature, invert_axes=True)


    def arrhenius_fit(self, subplot_ax, temperature, conductivity,
                  colorbar:bool=True, ax_sci_notation = None, scientific_limit=None):
        log.info("Creating a fitted Arrhenius plot")
    def compose_arrgenius_subplot(self, plots_list):pass #TODO

