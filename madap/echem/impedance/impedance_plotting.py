from matplotlib import pyplot as plt
from madap import logger
from plotting import Plots
from matplotlib.lines import Line2D

log = logger.get_logger("impedance_plotting")

class ImpedancePlotting(Plots):
    # def __init__(self) -> None:
    #     super().__init__()

    def nyquist(self, ax, frequency, real_impedance, imaginary_impedance, colorbar:bool=True,
                scientific_label:int=3, legend_label=None, color_map:str="viridis"):

        log.info("Creating Nyquist plot")
        nyquist_plot = ax.scatter(real_impedance, -imaginary_impedance, c=frequency,
                        cmap=color_map,rasterized=True,label=f"{legend_label} [V]")

        self.plot_identity(ax, xlabel=r"Z' $[\Omega]$", ylabel=r"-Z'' $[\Omega]$", x_lim=[0, max(real_impedance)],
                           y_lim=[0, max(-imaginary_impedance)])

        if legend_label:
            _, labels = ax.get_legend_handles_labels()
            new_handles= [Line2D([0], [0], marker='o', markerfacecolor="black", markeredgecolor="black", markersize=3, ls='')]
            ax.legend(new_handles, labels, loc="upper left")

        if colorbar:
            self.add_colorbar(nyquist_plot, ax, scientific_label)


    def bode(self, ax, frequency, real_impedance, imaginary_impedance, phase_shift):
        log.info("Creating Bode plot")
        pass

    def nyquist_fit(self, ax, frequency, real_impedance, imaginary_impedance, Z_fit,
                colorbar:bool=True, scientific_label:int=3, legend_label=None, color_map:str="viridis"):
        log.info("Creating a fitted Nyquist plot")
        pass

    def residual(self, ax, frequency, real_res, imag_res):
        log.info("Creating a residual plot")
        pass

