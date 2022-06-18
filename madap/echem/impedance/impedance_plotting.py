from cgitb import handler
from matplotlib import pyplot as plt
from madap import logger
from plotting import Plots
from matplotlib.lines import Line2D
import numpy as np


log = logger.get_logger("impedance_plotting")

class ImpedancePlotting(Plots):
    # def __init__(self) -> None:
    #     super().__init__()

    def nyquist(self, ax, frequency, real_impedance, imaginary_impedance, colorbar:bool=True,
                scientific_label:int=3, legend_label=False, voltage:float = None, color_map:str="viridis"):
        """Sets up a Nyquist plots

        Args:
            ax (AxesSubplot): The ax of the subplot
            frequency (pandas.core.series.Series): The series with the frequency
            real_impedance (pandas.core.series.Series): The Series with Real Impedance
            imaginary_impedance (pandas.core.series.Series): The series with the imaginary impedance
            colorbar (bool, optional): Whether or not a colorbar is desired. Defaults to True.
            scientific_label (int, optional): Scientific notation will be used for numbers
            outside the range.Defaults to 3.
            legend_label (str, optional): Label of the legend. Defaults to None.
            color_map (str, optional): Colormap to be used . Defaults to "viridis".
        """

        log.info("Creating Nyquist plot")
        nyquist_plot = ax.scatter(real_impedance, -imaginary_impedance, c=frequency,
                        cmap=color_map,rasterized=True,label=f"v = {voltage}[V]")

        self.plot_identity(ax, xlabel=r"Z' $[\Omega]$", ylabel=r"-Z'' $[\Omega]$",
                               x_lim=[0, max(real_impedance)],
                               y_lim=[0, max(-imaginary_impedance)])

        if legend_label:
            _, labels = ax.get_legend_handles_labels()
            new_handles= [Line2D([0], [0], marker='o',
                          markerfacecolor="black",
                          markeredgecolor="black", markersize=3, ls='')]
            ax.legend(new_handles, labels, loc="upper left")

        if colorbar:
            self.add_colorbar(nyquist_plot, ax, scientific_label)


    def bode(self, ax, frequency, real_impedance, imaginary_impedance, phase_shift):
        log.info("Creating Bode plot")
        pass

    def nyquist_fit(self, ax, frequency, real_impedance, imaginary_impedance, Z_fit, chi, suggested_circuit,
                colorbar:bool=True, scientific_label:int=3, legend_label=False, voltage:float = None, color_map:str="viridis"):
        
        log.info("Creating a fitted Nyquist plot")
        
        nyquist = ax.scatter(real_impedance, -imaginary_impedance, c=frequency,
                        cmap=color_map,rasterized=True,label=fr" v = {voltage}[V], $\chi$={np.format_float_scientific(chi, 3)}")

        nyquist_fit = ax.plot(np.real(Z_fit), -np.imag(Z_fit), label=f"Fitted with {suggested_circuit}", color="k")

        self.plot_identity(ax, xlabel=r"Z' $[\Omega]$", ylabel=r"-Z'' $[\Omega]$",
                               x_lim=[0, max(real_impedance)],
                               y_lim=[0, max(-imaginary_impedance)])

        if legend_label:
            _, labels = ax.get_legend_handles_labels()
            new_handles= [Line2D([0], [0], marker='o',
                          markerfacecolor="black",
                          markeredgecolor="black", markersize=3, ls=''),
                          Line2D([0], [0],
                          color="black", markersize=3, lw=1)]
            ax.legend(new_handles, labels, loc="upper left")

        if colorbar:
            self.add_colorbar(nyquist, ax, scientific_label)

    def residual(self, ax, frequency, real_res, imag_res):
        log.info("Creating a residual plot")
        pass

