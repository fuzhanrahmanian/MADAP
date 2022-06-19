from cgitb import handler
from matplotlib import pyplot as plt
from madap import logger
from plotting import Plots
from matplotlib.lines import Line2D
import matplotlib.colors as mcl
import numpy as np


log = logger.get_logger("impedance_plotting")

class ImpedancePlotting(Plots):
    # def __init__(self) -> None:
    #     super().__init__()

    def nyquist(self, ax, frequency, real_impedance, imaginary_impedance, colorbar:bool=True,
                ax_sci_notation = None, scientific_limit=None, scientific_label_colorbar=False,
                legend_label=False,voltage:float = None, color_map:str="viridis", norm_color=None):
        """Sets up a Nyquist plots

        Args:
            ax (AxesSubplot): The ax of the subplot
            frequency (pandas.core.series.Series): The series with the frequency
            real_impedance (pandas.core.series.Series): The Series with Real Impedance
            imaginary_impedance (pandas.core.series.Series): The series with the imaginary impedance
            colorbar (bool, optional): Whether or not a colorbar is desired. Defaults to True.
            ax_sci_notation (str, optiopnal): whether or not an axis should be written with
                scientific notation. It can be 'x', 'y', 'both' or None.
            scientific_label (optional): Scientific notation will be used for numbers
                outside the range.Defaults to None.
            legend_label (str, optional): Label of the legend. Defaults to None.
            voltage (float, optional): whether or not the applied voltage should be added to legend.
            color_map (str, optional): Colormap to be used . Defaults to "viridis".
        """

        log.info("Creating Nyquist plot")


        norm = mcl.LogNorm(vmin=min(frequency), vmax=max(frequency)) if norm_color else None

        nyquist_plot = ax.scatter(real_impedance, -imaginary_impedance, c=frequency, norm=norm,
                        cmap=color_map, rasterized=True,label=f"v = {voltage}[V]")

        nyquist_plot.set_clim(min(frequency), max(frequency))


        self.plot_identity(ax, xlabel=r"Z' $[\Omega]$", ylabel=r"-Z'' $[\Omega]$",
                               x_lim=[0, max(real_impedance)],
                               y_lim=[0, max(-imaginary_impedance)], ax_sci_notation=ax_sci_notation,
                               scientific_limit=scientific_limit)

        if (legend_label and voltage != None):
            _, labels = ax.get_legend_handles_labels()
            new_handles= [Line2D([0], [0], marker='o',
                          markerfacecolor="black",
                          markeredgecolor="black", markersize=3, ls='')]
            ax.legend(new_handles, labels, loc="upper left")

        if colorbar:
            self.add_colorbar(nyquist_plot, ax, scientific_label_colorbar, scientific_limit=scientific_limit,
            colorbar_label=r"f $[Hz]$")



    def bode(self, ax, frequency, real_impedance, imaginary_impedance, phase_shift):
        log.info("Creating Bode plot")
        pass

    def nyquist_fit(self, ax, frequency, real_impedance, imaginary_impedance, Z_fit, chi, suggested_circuit,
                    colorbar:bool=True, ax_sci_notation = None, scientific_limit=None, scientific_label_colorbar=False,
                    legend_label=False,voltage:float = None, color_map:str="viridis", norm_color=None):

        log.info("Creating a fitted Nyquist plot")


        nyquist_label = fr" v = {voltage}[V], $\chi$={np.format_float_scientific(chi, 3)}" if voltage else fr"$\chi$={np.format_float_scientific(chi, 3)}"

        norm = mcl.LogNorm(vmin=min(frequency), vmax=max(frequency)) if norm_color else None
        nyquist_plot = ax.scatter(real_impedance, -imaginary_impedance, c=frequency, norm=norm,
                        cmap=color_map,rasterized=True,label=nyquist_label)

        ax.plot(np.real(Z_fit), -np.imag(Z_fit), label=f"Fitted with {suggested_circuit}", color="k")

        self.plot_identity(ax, xlabel=r"Z' $[\Omega]$", ylabel=r"-Z'' $[\Omega]$",
                               x_lim=[0, max(real_impedance)],
                               y_lim=[0, max(-imaginary_impedance)], ax_sci_notation=ax_sci_notation,
                               scientific_limit=scientific_limit)

        if legend_label:
            _, labels = ax.get_legend_handles_labels()
            new_handles= [Line2D([0], [0], marker='o',
                          markerfacecolor="black",
                          markeredgecolor="black", markersize=3, ls=''),
                          Line2D([0], [0],
                          color="black", markersize=3, lw=1)]
            ax.legend(new_handles, labels, loc="upper left")

        if colorbar:
            self.add_colorbar(nyquist_plot, ax, scientific_label_colorbar, scientific_limit=scientific_limit)


    def residual(self, ax, frequency, res_real, res_imag, log_scale='x', ax_sci_notation = None,
                 scientific_limit:int=3):

        log.info("Creating a residual plot")
        ax.plot(frequency, res_real, label=r"$\Delta_{real}$", color="#453781ff", linestyle="--", marker='o')
        ax.plot(frequency, res_imag, label=r"$\Delta_{imaginary}$", color="#20a387ff", linestyle="--", marker='o')

        self.plot_identity(ax, xlabel=r"f $[Hz]$", ylabel=r"$\Delta$(residuals)",
                               #x_lim=[min(np.log(frequency)), max(np.log(frequency))],
                               #y_lim=[0, max(max(res_real), max(res_imag))]
                                ax_sci_notation=ax_sci_notation,
                                scientific_limit=scientific_limit, log_scale=log_scale)
        ax.legend(loc="lower right")


