
import numpy as np
from matplotlib import pyplot as plt
from madap.logger import logger
from madap.plotting.plotting import Plots


log = logger.get_logger("voltammetry_plotting")

class VoltammetryPlotting(Plots):

    def __init__(self, current, time, voltage,
                 electrode_area, mass_of_active_material,
                 cumulative_charge, procedure_type,
                 applied_voltage = None,
                 applied_current = None) -> None:
        """This class defines the plotting of the cyclic amperometry method.
        
        Args:
            current (list): list of currents
            time (list): list of times
            voltage (list): list of voltages
            applied_voltage (float): applied voltage
            electrode_area (float): area of active material
            mass_of_active_material (float): mass of active material
        """
        super().__init__()
        self.procedure_type = procedure_type
        self.current = current
        self.time = time
        self.voltage = voltage
        self.applied_voltage = applied_voltage
        self.electrode_area = electrode_area
        self.mass_of_active_material = mass_of_active_material
        self.cumulative_charge = cumulative_charge
        self.applied_current = applied_current


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
        elif self.electrode_area is not None:
            # Change the unit of current from mA to mA/cm^2
            current_mA = [i/self.electrode_area for i in self.current]
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
        if self.procedure_type == "Voltammetry_CA":
            if self.applied_voltage is None:
                measured_voltage = np.mean(self.voltage)
            else:
                measured_voltage = self.applied_voltage
            label = f"{measured_voltage:.2f} V"
        elif self.procedure_type == "Voltammetry_CP":
            measured_current = np.abs(np.mean(self.current))
            label = f"{measured_current:.2e} A"

        time_h = [i/3600 for i in self.time]
        # Change the unit of charge from As to mAh
        charge, y_label = self._charge_conversion()

        subplot_ax.scatter(time_h, charge, label=label, s=3)
        self.plot_identity(subplot_ax, xlabel="Time (h)", ylabel=y_label,
                           ax_sci_notation="both", x_lim=[0, max(time_h)], y_lim=[0, max(charge)])
        # If the charge increases the legend is placed in the lower right corner
        # If the charge decreases the legend is placed in the upper right corner
        if self.cumulative_charge[-1] > self.cumulative_charge[0]:
            subplot_ax.legend(loc="lower right")
        else:
            subplot_ax.legend(loc="upper right")

    def Cottrell(self, subplot_ax, diffusion_coefficient, best_fit_diffusion = None):
        """Plot the Cottrell plot.
        Args:
            subplot_ax (matplotlib.axes): axis to which the plot should be added
        """

        log.info("Creating Cottrell plot")

        x_data = (self.time)**(-0.5)
        if self.procedure_type == "Voltammetry_CA":
            x_vals = np.array([x_data[best_fit_diffusion['start']], x_data[best_fit_diffusion['end']]])
            y_data = self.current
            y_vals = best_fit_diffusion['slope']*x_vals + best_fit_diffusion['intercept']
            subplot_ax.scatter(x_data[1:], y_data[1:], s=3, label="D="+f"{diffusion_coefficient:.2e} cm^2/s")
            subplot_ax.plot(x_vals, y_vals, color="#f48024", linewidth=2, linestyle='--', label="Diffusion coefficient")
            y_label = "Current (A)"
        elif self.procedure_type == "Voltammetry_CP":
            y_data = self.voltage
            subplot_ax.scatter(x_data[1:], y_data[1:], s=3, label="D="+f"{diffusion_coefficient:.2e}"+r"$\cdot \tau$"+" cm^2/s")
            y_label = "Voltage (V)"

        self.plot_identity(subplot_ax, xlabel=r"$t^{-1/2}  [s^{-1/2}]$", ylabel=y_label,
                            ax_sci_notation="both", x_lim=[0, max(x_data[1:])], y_lim=[min(y_data), max(y_data[1:])])
        if np.mean(self.current) > 0:
            subplot_ax.legend(loc="upper right")
        else:
            subplot_ax.legend(loc="lower right")

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

    def Voltage_Profile(self, subplot_ax):
        """Plot the voltage profile plot.

        Args:
            subplot_ax (matplotlib.axes): axis to which the plot should be added
        """
        log.info("Creating voltage profile plot")

        charge, x_label = self._charge_conversion()
        subplot_ax.scatter(charge, self.voltage, s=3)
        self.plot_identity(subplot_ax, xlabel=x_label, ylabel="Voltage (V)",
                           ax_sci_notation="both", x_lim=[min(charge), max(charge)], y_lim=[min(self.voltage), max(self.voltage)])


    def Potential_Rate(self, subplot_ax, dVdt, transition_values, tao_initial):
        """Plot the potential rate plot.
        
        Args:
            subplot_ax (matplotlib.axes): axis to which the plot should be added
        """
        log.info("Creating potential rate, dVdt plot")
        
        subplot_ax.plot(self.time, dVdt, linewidth=1)
        #subplot_ax.plot(self.time, dVdt_smoothed, color="#f48024", linewidth=2, label="Smoothed")
        self.plot_identity(subplot_ax, xlabel="Time (s)", ylabel="dV/dt (V/s)",
                           ax_sci_notation="y", x_lim=[0, max(self.time)], y_lim=[min(dVdt), max(dVdt)*1.1])
        #subplot_ax.legend(loc="upper right")
        # Define a textbox under the legend with the transition and stabilization values
        if transition_values:
            transition_times = [round(i,2) for i in transition_values.keys()]
            textbox_text = r"$\tau_{stabilization}$"+f"={round(tao_initial,2)} [s]\n"+r"$\tau_{transition} \in $"+"{"+f"{str(transition_times)[1:-1]}"+"} [s]"
        else:
            textbox_text = r"$\tau_{stabilization}$"+f"={round(tao_initial,2)} [s]"

        if np.mean(self.current) < 0:
            subplot_ax.text(0.95, 0.05, textbox_text, transform=subplot_ax.transAxes,
                            fontsize=7, verticalalignment='bottom', horizontalalignment='right')
        else:
            subplot_ax.text(0.5, 0.8, textbox_text, transform=subplot_ax.transAxes,
                        fontsize=7, verticalalignment='bottom', horizontalalignment='left')

    def Differential_Capacity(self, subplot_ax):
        pass 
    
    def CP(self, subplot_ax):
        """Plot the voltage plot.

        Args:
            subplot_ax (matplotlib.axes): axis to which the plot should be added
        """
        log.info("Creating voltage plot")
        if self.applied_current:
            subplot_ax.scatter(self.time, self.voltage, s=3, label=f"{np.abs(np.mean(self.current)):.2e} A")
        else:
            subplot_ax.scatter(self.time, self.voltage, s=3)
        self.plot_identity(subplot_ax, xlabel="Time (s)", ylabel="Voltage (V)",
                            ax_sci_notation="x", x_lim=[0, max(self.time)], y_lim=[min(self.voltage)*0.6, max(self.voltage)*1.1])
        subplot_ax.legend(loc="upper right")
    def compose_volt_subplot(self, plots:list):
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
            return Exception(f"No plots for EIS were selected for plot {self.procedure_type}.")

        log.error("Maximum plots for EIS is exceeded.")
        return Exception(f"Maximum plots for EIS is exceeded for plot {self.procedure_type}.")


    def _charge_conversion(self):
        # Change the unit of charge from As to mAh
        cumulative_charge_mAh = [i*1e3/3600 for i in self.cumulative_charge]
        # Convert self.time from s to h
        if self.mass_of_active_material is not None:
            # Change the unit of current from A to mA/g
            charge = [i/self.mass_of_active_material for i in cumulative_charge_mAh]
            y_label = "Capacity (mAh/g)"
        elif self.electrode_area is not None:
            # Change the unit of current from A to mA/cm^2
            charge = [i/self.electrode_area for i in cumulative_charge_mAh]
            y_label = "Capacity (mAh/cm^2)"
        else:
            charge = cumulative_charge_mAh
            y_label = "Charge (mAh)"
        return charge, y_label