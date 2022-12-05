"""Chrono Potentiometric Plotting module."""
import numpy as np
import matplotlib.colors as mcl
from matplotlib import pyplot as plt
from matplotlib.lines import Line2D

from madap.logger import logger
from madap.plotting.plotting import Plots


log = logger.get_logger("voltammetry_CP_plotting")

class VoltammetryCP(Plots):
    """General Plotting class for galvanostatic chrono potentiostatic method.

    Args:
        Plots (class): Parent class for plotting all methods.
    """
    def __init__(self) -> None:
        super().__init__()
        self.plot_type = "voltammetry"

    def chrono_potentiometric(self):pass


    def galvanostatic_charge(self):pass


    def differential_capacity(self):pass


    def compose_cp_subplot(self, plots:list):
        """Compose the CP subplot

        Args:
            plots (list): List of plots to be composed.

        Returns:
            fig, ax: Figure and axis of the subplot.
        """

        plt.close('all')
        if len(plots)==1:
            fig = plt.figure(figsize=(3.5,3))
            spec = fig.add_gridspec(1, 1)
            ax = fig.add_subplot(spec[0,0])
            return fig, [ax]

        if len(plots) == 2:
            fig_size = 9 if ("nyquist" and "nyquist_fit") in plots else 8.5
            fig = plt.figure(figsize=(fig_size, 4))
            spec = fig.add_gridspec(1, 2)
            ax1 = fig.add_subplot(spec[0, 0])
            ax2= fig.add_subplot(spec[0, 1])
            return fig, [ax1, ax2]

        if len(plots) == 3:
            fig_size= 7 if ("nyquist" and "nyquist_fit" and "bode") in plots else 6.5
            fig = plt.figure(figsize=(fig_size, 5))
            spec = fig.add_gridspec(2, 2)
            if "residual" in plots:
                ax1 = fig.add_subplot(spec[0, 0])
                ax2 = fig.add_subplot(spec[0, 1])
                ax3 = fig.add_subplot(spec[1, :])
            else:
                ax1 = fig.add_subplot(spec[0, 0])
                ax2 = fig.add_subplot(spec[1, 0])
                ax3 = fig.add_subplot(spec[:, 1])
            return fig, [ax1, ax2, ax3]

        if len(plots) == 4:
            fig = plt.figure(figsize=(7.5, 6))
            spec = fig.add_gridspec(2, 2)
            ax1 = fig.add_subplot(spec[0, 0])
            ax2= fig.add_subplot(spec[0, 1])
            ax3 = fig.add_subplot(spec[1, 0])
            ax4 = fig.add_subplot(spec[1, 1])
            return fig, [ax1, ax2, ax3, ax4]

        if len(plots) == 0:
            log.error("No plots for EIS were selected.")
            return Exception(f"No plots for EIS were selected for plot {self.plot_type}.")

        log.error("Maximum plots for EIS is exceeded.")
        return Exception(f"Maximum plots for EIS is exceeded for plot {self.plot_type}.")
