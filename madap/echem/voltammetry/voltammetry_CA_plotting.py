
import numpy as np
from matplotlib import pyplot as plt
from madap.logger import logger
from madap.plotting.plotting import Plots


log = logger.get_logger("voltammetry_plotting")

class VoltammetryCAPlotting(Plots):

    def __init__(self) -> None:
        super().__init__()
        self.plot_type = "voltammetry_CA"

    def CA(self, subplot_ax, current, time, voltage, applied_voltage,
            area_of_active_material, mass_of_active_material):

        log.info("Creating CA plot")

        # Change the unit of current from A to mA
        current = [i*1e3 for i in current]

        # Change the seconds to hours
        time = [i/3600 for i in time]

        if mass_of_active_material is not None:
            # Change the unit of current from mA to mA/g7
            current = [i/mass_of_active_material for i in current]
            y_label = "Current (mA/g)"
        elif area_of_active_material is not None:
            # Change the unit of current from mA to mA/cm^2
            current = [i/area_of_active_material for i in current]
            y_label = "Current (mA/cm^2)"
        else:
            y_label = "Current (mA)"

        if applied_voltage is None:
            measured_voltage = np.mean(voltage)
        else:
            measured_voltage = applied_voltage

        # Plot a scatterplot where x is time and y is current with a label of applied voltage
        subplot_ax.scatter(time, current, label=f"{measured_voltage:.2f} V", s=4)
        self.plot_identity(subplot_ax, xlabel="Time (h)", ylabel=y_label, ax_sci_notation="x",
                           x_lim=[0, max(time)], y_lim=[0, max(current)])
        # If the current increases the legend is placed in the lower right corner
        # If the current decreases the legend is placed in the upper right corner
        if current[-1] > current[0]:
            subplot_ax.legend(loc="lower right")
        else:
            subplot_ax.legend(loc="upper right")

    def Log_CA(self, subplot_ax):
        pass

    def CC(self, subplot_ax):
        pass

    def Cotrell(self, subplot_ax):
        pass

    def Anson(self, subplot_ax):
        pass

    def compose_ca_subplot(self, plots:list):
        """ Compose the subplot for the CA plot.
        Args:
            plots (list): List of plots to be composed.

        Returns:
            fig, ax: Figure and axis of the subplot.
        """
        plt.close('all')
        if len(plots)==1:
            fig = plt.figure(figsize=(3,2.5))
            spec = fig.add_gridspec(1, 1)
            ax = fig.add_subplot(spec[0,0])
            return fig, [ax]

        if len(plots) == 2:
            fig_size = 8.5
            fig = plt.figure(figsize=(fig_size, 4))
            spec = fig.add_gridspec(1, 2)
            ax1 = fig.add_subplot(spec[0, 0])
            ax2= fig.add_subplot(spec[0, 1])
            return fig, [ax1, ax2]

        if len(plots) == 3:
            fig_size= 6.5
            fig = plt.figure(figsize=(fig_size, 5))
            spec = fig.add_gridspec(1, 3)
            ax1 = fig.add_subplot(spec[0, 0])
            ax2 = fig.add_subplot(spec[0, 1])
            ax3 = fig.add_subplot(spec[0, 2])
            return fig, [ax1, ax2, ax3]

        if len(plots) == 4:
            fig = plt.figure(figsize=(7.5, 6))
            spec = fig.add_gridspec(2, 2)
            ax1 = fig.add_subplot(spec[0, 0])
            ax2= fig.add_subplot(spec[0, 1])
            ax3 = fig.add_subplot(spec[1, 0])
            ax4 = fig.add_subplot(spec[1, 1])
            return fig, [ax1, ax2, ax3, ax4]
        
        if len(plots) == 5:
            fig = plt.figure(figsize=(7.5, 6))
            spec = fig.add_gridspec(2, 3)
            ax1 = fig.add_subplot(spec[0, 0])
            ax2= fig.add_subplot(spec[0, 1])
            ax3 = fig.add_subplot(spec[0, 2])
            ax4 = fig.add_subplot(spec[1, 0])
            ax5 = fig.add_subplot(spec[1, 1])
            return fig, [ax1, ax2, ax3, ax4, ax5]

        if len(plots) == 0:
            log.error("No plots for EIS were selected.")
            return Exception(f"No plots for EIS were selected for plot {self.plot_type}.")

        log.error("Maximum plots for EIS is exceeded.")
        return Exception(f"Maximum plots for EIS is exceeded for plot {self.plot_type}.")