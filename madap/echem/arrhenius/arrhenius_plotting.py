from madap import logger
from matplotlib import pyplot as plt
from matplotlib.lines import Line2D
import matplotlib.colors as mcl
import numpy as np
from plotting import Plots
from utils import utils


log = logger.get_logger("arrhenius_plotting")

class ArrheniusPlotting(Plots):

    def arrhenius(self, subplot_ax, temperatures, log_conductivity, inversted_scale_temperatures,
            ax_sci_notation = None, scientific_limit: int = 3):

        # log conductivity should have unit of S/cm
        log.info("Creating Arrhenius plot")
        subplot_ax2=subplot_ax.twiny()
        self.plot_identity(subplot_ax, xlabel=r"$\frac{1000}{T}$ $[K^{-1}]$",
                           ylabel=r"$\ln$($\sigma$) [$ln(S.cm^{-1})$]",
                           ax_sci_notation=ax_sci_notation,
                           scientific_limit=scientific_limit)

        subplot_ax2.scatter(temperatures, log_conductivity, s=10, c="#20a387ff", rasterized=True)
        self.plot_identity(subplot_ax2, xlabel="$T$ [\u00b0C]")
        self.set_xtick_for_two_axes(subplot_ax, subplot_ax2, ["%.1f" % ct for ct in inversted_scale_temperatures], temperatures, invert_axes=True)

    def arrhenius_fit(self, subplot_ax, temperatures, log_conductivity, inverted_scale_temperatures,
                    ln_conductivity_fit, activation, arrhenius_constant, r2_score,
                    ax_sci_notation = None, scientific_limit: int=3):

        log.info("Creating a fitted Arrhenius plot")
        subplot_ax2=subplot_ax.twiny()
        subplot_ax.plot(inverted_scale_temperatures, ln_conductivity_fit, c="#453781ff", linewidth=1, linestyle="--",
                        label=f" E  = {activation:.2f} [mJ.mol⁻¹] \n A  = {arrhenius_constant:.2f} [S.cm⁻¹] \n R² = {r2_score:.2f}")

        subplot_ax2.scatter(temperatures, log_conductivity, s=10, c="#20a387ff", rasterized=True)
        subplot_ax2.invert_xaxis()
        self.plot_identity(subplot_ax, xlabel=r"$\frac{1000}{T}$ $[K^{-1}]$",
                           ylabel=r"$\ln$($\sigma$) [$ln(S.cm^{-1})$]",
                           ax_sci_notation=ax_sci_notation,
                           scientific_limit=scientific_limit)
        subplot_ax.legend(loc="upper right", fontsize=5.5)

        self.plot_identity(subplot_ax2, xlabel="$T$ [\u00b0C]")

    def compose_arrhenius_subplot(self, plots:list):

        if len(plots)==1:
            fig = plt.figure(figsize=(3, 3)) # figsize=(7, 3)
            spec = fig.add_gridspec(1, 1)
            ax = fig.add_subplot(spec[0,0])
            return fig, [ax]

        elif len(plots) == 2:
            fig = plt.figure(figsize=(6, 3))
            spec = fig.add_gridspec(1, 2)
            ax1 = fig.add_subplot(spec[0, 0])
            ax2= fig.add_subplot(spec[0, 1])
            return fig, [ax1, ax2]

