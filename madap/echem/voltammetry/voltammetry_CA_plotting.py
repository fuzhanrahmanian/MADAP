
import numpy as np
from matplotlib import pyplot as plt
from madap.logger import logger
from madap.plotting.plotting import Plots


log = logger.get_logger("voltammetry_plotting")

class VoltammetryCAPlotting(Plots):

    def __init__(self, current, time, voltage, applied_voltage,
                 area_of_active_material, mass_of_active_material, cumulative_charge) -> None:
        """This class defines the plotting of the cyclic amperometry method.
        
        Args:
            current (list): list of currents
            time (list): list of times
            voltage (list): list of voltages
            applied_voltage (float): applied voltage
            area_of_active_material (float): area of active material
            mass_of_active_material (float): mass of active material
        """
        super().__init__()
        self.plot_type = "voltammetry_CA"
        self.current = current
        self.time = time
        self.voltage = voltage
        self.applied_voltage = applied_voltage
        self.area_of_active_material = area_of_active_material
        self.mass_of_active_material = mass_of_active_material
        self.cumulative_charge = cumulative_charge
    def CA(self, subplot_ax):
        """Plot the CA plot.
        
        Args:
            subplot_ax (matplotlib.axes): axis to which the plot should be added
        """
        log.info("Creating CA plot")

        # Change the unit of current from A to mA
        current_mA = [i*1e3 for i in self.current]
        if self.mass_of_active_material is not None:
            # Change the unit of current from mA to mA/g7
            current_mA = [i/self.mass_of_active_material for i in self.current]
            y_label = "Current (mA/g)"
        elif self.area_of_active_material is not None:
            # Change the unit of current from mA to mA/cm^2
            current_mA = [i/self.area_of_active_material for i in self.current]
            y_label = "Current (mA/cm^2)"
        else:
            y_label = "Current (mA)"

        if self.applied_voltage is None:
            measured_voltage = np.mean(self.voltage)
        else:
            measured_voltage = self.applied_voltage

        # Plot a scatterplot where x is time and y is current with a label of applied voltage
        subplot_ax.scatter(self.time, current_mA, label=f"{measured_voltage:.2f} V", s=3)
        self.plot_identity(subplot_ax, xlabel="Time (s)", ylabel=y_label, ax_sci_notation="x",
                           x_lim=[0, max(self.time)], y_lim=[0, max(current_mA)])
        # If the current increases the legend is placed in the lower right corner
        # If the current decreases the legend is placed in the upper right corner
        if current_mA[-1] > current_mA[0]:
            subplot_ax.legend(loc="lower right")
        else:
            subplot_ax.legend(loc="upper right")

    def Log_CA(self, subplot_ax, y_data, reaction_rate, reaction_order,best_fit_reaction_rate):
        """Plot the Log CA plot.
        
        Args:
            subplot_ax (matplotlib.axes): axis to which the plot should be added
        """
        log.info("Creating Log CA plot")
        if reaction_order == 1:
            y_label = "Log(Current) (A)"
            label = r"$\kappa$"+f"={reaction_rate:.2e} 1/s"
        elif reaction_order == 2:
            y_label = "1/Current (1/A)"
            label = r"$\kappa$"+f"{reaction_rate:.2e}"+r"$cm^3/mol/s$"
        
        x_vals = np.array([self.time[best_fit_reaction_rate['start']], self.time[best_fit_reaction_rate['end']]])
        y_vals = best_fit_reaction_rate['slope']*x_vals + best_fit_reaction_rate['intercept']
        subplot_ax.plot(x_vals, y_vals, color="#f48024", linewidth=2, linestyle='--', label="Instantaneous rate")
        # MArk the instantaneous rate on the plot
        #subplot_ax.scatter(x_vals, y_vals, color="#660d33", s=5, marker='x', linewidth=2, label="Intercept")
        subplot_ax.scatter(self.time[1:], y_data, s=3, label=label)
        self.plot_identity(subplot_ax, xlabel="Time (s)", ylabel=y_label, ax_sci_notation="x",
                            x_lim=[0, max(self.time)], y_lim=[min(y_data)*0.6, max(y_data)*1.1])
        subplot_ax.legend(loc="upper right")

    def CC(self, subplot_ax):
        """Plot the CC plot.
        
        Args:
            subplot_ax (matplotlib.axes): axis to which the plot should be added
        """
        log.info("Creating CC plot")

        if self.applied_voltage is None:
            measured_voltage = np.mean(self.voltage)
        else:
            measured_voltage = self.applied_voltage

        subplot_ax.scatter(self.time, self.cumulative_charge, label=f"{measured_voltage:.2f} V", s=3)
        self.plot_identity(subplot_ax, xlabel="Time (s)", ylabel="Charge (C)",
                           ax_sci_notation="both", x_lim=[0, max(self.time)], y_lim=[0, max(self.cumulative_charge)])
        # If the charge increases the legend is placed in the lower right corner
        # If the charge decreases the legend is placed in the upper right corner
        if self.cumulative_charge[-1] > self.cumulative_charge[0]:
            subplot_ax.legend(loc="lower right")
        else:
            subplot_ax.legend(loc="upper right")

    def Cotrell(self, subplot_ax, diffusion_coefficient, best_fit_diffusion):
        """Plot the Cotrell plot.
        Args:
            subplot_ax (matplotlib.axes): axis to which the plot should be added
        """

        log.info("Creating Cotrell plot")

        x_data = (self.time)**(-0.5)
        y_data = self.current

        x_vals = np.array([x_data[best_fit_diffusion['start']], x_data[best_fit_diffusion['end']]])
        y_vals = best_fit_diffusion['slope']*x_vals + best_fit_diffusion['intercept']


        subplot_ax.scatter(x_data[1:], y_data[1:], s=3, label="D="+f"{diffusion_coefficient:.2e} cm^2/s")
        subplot_ax.plot(x_vals, y_vals, color="#f48024", linewidth=2, linestyle='--', label="Diffusion coefficient")
        self.plot_identity(subplot_ax, xlabel=r"$t^{-1/2}  [s^{-1/2}]$", ylabel="Current (A)",
                            ax_sci_notation="both", x_lim=[0, max(x_data[1:])], y_lim=[0, max(y_data[1:])])
        subplot_ax.legend(loc="upper right")

    def Anson(self, subplot_ax, diffusion_coefficient):
        """Plot the Anson plot.

        Args:
            subplot_ax (matplotlib.axes): axis to which the plot should be added
        """

        log.info("Creating Anson plot")
        x_data = (self.time)**(0.5)
        y_data = self.cumulative_charge
        subplot_ax.scatter(x_data, y_data, s=3, label="D="+f"{diffusion_coefficient:.2e} cm^2/s")
        self.plot_identity(subplot_ax, xlabel=r"$t^{1/2}  [s^{1/2}]$", ylabel="Charge (C)",
                            ax_sci_notation="both", x_lim=[0, max(x_data)], y_lim=[0, max(y_data)])
        subplot_ax.legend(loc="upper right")

    def Voltage(self, subplot_ax):
        """Plot the voltage plot.

        Args:
            subplot_ax (matplotlib.axes): axis to which the plot should be added
        """
        log.info("Creating voltage plot")
        subplot_ax.scatter(self.time, self.voltage, s=3)
        self.plot_identity(subplot_ax, xlabel="Time (s)", ylabel="Voltage (V)",
                            ax_sci_notation="x", x_lim=[0, max(self.time)], y_lim=[min(self.voltage)*0.6, max(self.voltage)*1.1])

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
            fig_size = 5.5
            fig = plt.figure(figsize=(fig_size, 2.5))
            spec = fig.add_gridspec(1, 2)
            ax1 = fig.add_subplot(spec[0, 0])
            ax2= fig.add_subplot(spec[0, 1])
            return fig, [ax1, ax2]

        if len(plots) == 3:
            fig_size= 8
            fig = plt.figure(figsize=(fig_size, 2.5))
            spec = fig.add_gridspec(1, 3)
            ax1 = fig.add_subplot(spec[0, 0])
            ax2 = fig.add_subplot(spec[0, 1])
            ax3 = fig.add_subplot(spec[0, 2])
            return fig, [ax1, ax2, ax3]

        if len(plots) == 4:
            fig = plt.figure(figsize=(6, 5))
            spec = fig.add_gridspec(2, 2)
            ax1 = fig.add_subplot(spec[0, 0])
            ax2= fig.add_subplot(spec[0, 1])
            ax3 = fig.add_subplot(spec[1, 0])
            ax4 = fig.add_subplot(spec[1, 1])
            return fig, [ax1, ax2, ax3, ax4]
        
        if len(plots) == 5:
            fig = plt.figure(figsize=(9, 5))
            spec = fig.add_gridspec(2, 3)
            ax1 = fig.add_subplot(spec[0, 0])
            ax2= fig.add_subplot(spec[0, 1])
            ax3 = fig.add_subplot(spec[0, 2])
            ax4 = fig.add_subplot(spec[1, 0])
            ax5 = fig.add_subplot(spec[1, 1])
            return fig, [ax1, ax2, ax3, ax4, ax5]
        
        if len(plots) == 6:
            fig = plt.figure(figsize=(9, 5))
            spec = fig.add_gridspec(2, 3)
            ax1 = fig.add_subplot(spec[0, 0])
            ax2= fig.add_subplot(spec[0, 1])
            ax3 = fig.add_subplot(spec[0, 2])
            ax4 = fig.add_subplot(spec[1, 0])
            ax5 = fig.add_subplot(spec[1, 1])
            ax6 = fig.add_subplot(spec[1, 2])
            return fig, [ax1, ax2, ax3, ax4, ax5, ax6]

        if len(plots) == 0:
            log.error("No plots for EIS were selected.")
            return Exception(f"No plots for EIS were selected for plot {self.plot_type}.")

        log.error("Maximum plots for EIS is exceeded.")
        return Exception(f"Maximum plots for EIS is exceeded for plot {self.plot_type}.")