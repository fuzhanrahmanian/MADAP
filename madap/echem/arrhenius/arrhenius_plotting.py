from madap import logger
from matplotlib import pyplot as plt
from matplotlib.lines import Line2D
import matplotlib.colors as mcl
import numpy as np
from plotting import Plots


log = logger.get_logger("arrhenius_plotting")

class ArrheniusPlotting(Plots):
    def arrhenius(self, subplot_ax, temperature, log_conductivity,
            ax_sci_notation = None, scientific_limit: int = 3):

        # log conductivity should have unit of S/cm
        log.info("Creating Arrhenius plot")
        x_temp_in_kelvin = [1000/(temp + 273.15) for temp in temperature]
        subplot_ax.scatter(x_temp_in_kelvin, log_conductivity, s=10, c="black", rasterized=True)

        ax2=subplot_ax.twiny()
        self.plot_identity(subplot_ax, xlabel=r"$\frac{1000}{T}$ $[K^{-1}]$",
                           ylabel=r"$\log$($\sigma$) [$S.cm^{-1}$]",
                           #x_lim=[min(x_temp_in_kelvin), max(x_temp_in_kelvin)],
                           ax_sci_notation=ax_sci_notation,
                           scientific_limit=scientific_limit)
        #subplot_ax.set_xlim([min(x_temp_in_kelvin), max(x_temp_in_kelvin)])

        self.plot_identity(ax2, xlabel="$T$ [\u00b0C]")#, x_lim=[min(temperature), max(temperature)], step_size_x=10)
        ax2.set_xlim(subplot_ax.get_xlim())
        
        ax2.set_xticklabels(temperature)
    
# plt.xlabel(r"$\frac{LiPF_{6}}{EC + PC + EMC}$ [$\frac{mol}{Kg}$]", fontdict=dict(size=12.5)) #, weight="bold")
# plt.ylabel(r"$\sigma$ [$\frac{S}{cm}$]", fontdict=dict(size=12.5)) #, weight="bold")

        
    def arrhenius_fit(self, subplot_ax, temperature, conductivity,
                  colorbar:bool=True, ax_sci_notation = None, scientific_limit=None):
        log.info("Creating a fitted Arrhenius plot")
    def compose_arrgenius_subplot(self, plots_list):pass #TODO
        
