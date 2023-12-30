""" This module defines the plotting of the cyclic voltammetry studies. """
import numpy as np

from matplotlib import pyplot as plt
from matplotlib import gridspec
from matplotlib.legend_handler import HandlerTuple

from madap.logger import logger
from madap.utils import utils
from madap.plotting.plotting import Plots


log = logger.get_logger("voltammetry_plotting")

class VoltammetryPlotting(Plots):
    """This class defines the plotting of the cyclic voltammetry studies."""
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


    def CA(self, subplot_ax, x_lim_min=0 ,y_lim_min=0, legend=True):
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
        if legend:
            subplot_ax.scatter(self.time, current_mA, label=f"{measured_voltage:.2f} V", s=2, color="#435a82")
        else:
            subplot_ax.plot(self.time, current_mA, linewidth=0.9, color="#435a82")
        if y_lim_min == "auto":
            y_lim_min = min(current_mA)
        if x_lim_min == "auto":
            x_lim_min = min(self.time)

        self.plot_identity(subplot_ax, xlabel="Time (s)", ylabel=y_label, ax_sci_notation="x",
                           x_lim=[x_lim_min, max(self.time)], y_lim=[y_lim_min, max(current_mA)])
        # If the current increases the legend is placed in the lower right corner
        # If the current decreases the legend is placed in the upper right corner
        if current_mA[-1] > current_mA[0]:
            subplot_ax.legend(loc="lower right")
        else:
            subplot_ax.legend(loc="upper right")


    def log_CA(self, subplot_ax, y_data, reaction_rate, reaction_order,best_fit_reaction_rate):
        """Plot the Log CA plot.

        Args:
            subplot_ax (matplotlib.axes): axis to which the plot should be added
        """
        log.info("Creating Log CA plot")
        if reaction_order == 0:
            y_label = "Current (A)"
            label = r"$\kappa$"+f"={reaction_rate:.2e} A/s"
        elif reaction_order == 1:
            y_label = "Log(Current) (A)"
            label = r"$\kappa$"+f"={reaction_rate:.2e} 1/s"
        elif reaction_order == 2:
            y_label = "1/Current (1/A)"
            label = r"$\kappa$"+f"{reaction_rate:.2e}"+r"$cm^3/mol/s$"

        x_vals = np.array([self.time[best_fit_reaction_rate['start']], self.time[best_fit_reaction_rate['end']]])
        y_vals = best_fit_reaction_rate['slope']*x_vals + best_fit_reaction_rate['intercept']
        subplot_ax.plot(x_vals, y_vals, color="#a8212a", linewidth=2, linestyle='--', label="Instantaneous rate")
        # MArk the instantaneous rate on the plot
        #subplot_ax.scatter(x_vals, y_vals, color="#660d33", s=5, marker='x', linewidth=2, label="Intercept")
        subplot_ax.scatter(self.time[1:], y_data, s=2, label=label, color="#396b82", zorder=0)
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
        charge = np.abs(charge)
        subplot_ax.scatter(time_h, charge, label=label, s=2, color="#2e8b7e")
        self.plot_identity(subplot_ax, xlabel="Time (h)", ylabel=y_label,
                           ax_sci_notation="both", x_lim=[0, max(time_h)], y_lim=[0, max(charge)])
        # If the charge increases the legend is placed in the lower right corner
        # If the charge decreases the legend is placed in the upper right corner
        subplot_ax.legend(loc="lower right")


    def cottrell(self, subplot_ax, diffusion_coefficient, best_fit_diffusion = None):
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
            subplot_ax.scatter(x_data[1:], y_data[1:], s=2, label="D="+f"{diffusion_coefficient:.2e} cm^2/s", color="#4a467b")
            subplot_ax.plot(x_vals, y_vals, color="#a8212a", linewidth=1.5, linestyle='--', label="Diffusion coefficient")
            y_label = r"$I (A)$"
        elif self.procedure_type == "Voltammetry_CP":
            y_data = self.voltage
            subplot_ax.scatter(x_data[1:], y_data[1:], s=2, label="D="+f"{diffusion_coefficient:.2e}"+r"$\cdot \tau$"+" cm^2/s", color="#4a467b")
            y_label = r"$Voltage (V)$"

        self.plot_identity(subplot_ax, xlabel=r"$t^{-1/2}  [s^{-1/2}]$", ylabel=y_label,
                            ax_sci_notation="both", x_lim=[0, max(x_data[1:])], y_lim=[min(y_data), max(y_data[1:])])
        if np.mean(self.current) > 0:
            subplot_ax.legend(loc="upper right")
        else:
            subplot_ax.legend(loc="lower right")


    def anson(self, subplot_ax, diffusion_coefficient):
        """Plot the Anson plot.

        Args:
            subplot_ax (matplotlib.axes): axis to which the plot should be added
        """

        log.info("Creating Anson plot")
        x_data = (self.time)**(0.5)
        y_data = self.cumulative_charge
        subplot_ax.scatter(x_data, y_data, s=2, label="D="+f"{diffusion_coefficient:.2e} cm^2/s", color="#317a80")
        self.plot_identity(subplot_ax, xlabel=r"$t^{1/2}  [s^{1/2}]$", ylabel="Charge (C)",
                            ax_sci_notation="both", x_lim=[0, max(x_data)], y_lim=[0, max(y_data)])
        subplot_ax.legend(loc="upper left")


    def voltage_profile(self, subplot_ax):
        """Plot the voltage profile plot.

        Args:
            subplot_ax (matplotlib.axes): axis to which the plot should be added
        """
        log.info("Creating voltage profile plot")

        charge, x_label = self._charge_conversion()
        charge = np.abs(charge)
        subplot_ax.scatter(charge, self.voltage, s=3, color="#3b9f7a")
        self.plot_identity(subplot_ax, xlabel=x_label, ylabel="Voltage (V)",
                           ax_sci_notation="both", x_lim=[min(charge), max(charge)], y_lim=[min(self.voltage), max(self.voltage)])


    def potential_rate(self, subplot_ax, dVdt, transition_values, tao_initial):
        """Plot the potential rate plot.

        Args:
            subplot_ax (matplotlib.axes): axis to which the plot should be added
            dVdt (list): list of potential rates
            transition_values (dict): dictionary of transition values
            tao_initial (float): initial stabilization time
        """
        log.info("Creating potential rate, dVdt plot")

        subplot_ax.plot(self.time, dVdt, linewidth=2, color="#317a80")
        #subplot_ax.plot(self.time, dVdt_smoothed, color="#f48024", linewidth=2, label="Smoothed")
        self.plot_identity(subplot_ax, xlabel="Time (s)", ylabel="dV/dt (V/s)",
                           ax_sci_notation="y", x_lim=[0, max(self.time)], y_lim=[min(dVdt), max(dVdt)*1.1])
        #subplot_ax.legend(loc="upper right")
        # Define a textbox under the legend with the transition and stabilization values
        if transition_values:
            transition_times = [round(i,2) for i in transition_values.keys()]
            textbox_text = r"$\tau_{stabilization}$"+f"={round(tao_initial,2)} [s]\n"+\
                r"$\tau_{transition} \in $"+"{"+f"{str(transition_times)[1:-1]}"+"} [s]"
        else:
            textbox_text = r"$\tau_{stabilization}$"+f"={round(tao_initial,2)} [s]"

        if np.mean(self.current) < 0:
            subplot_ax.text(0.95, 0.05, textbox_text, transform=subplot_ax.transAxes,
                            fontsize=8, verticalalignment='bottom', horizontalalignment='right')
        else:
            subplot_ax.text(0.05, 0.8, textbox_text, transform=subplot_ax.transAxes,
                        fontsize=8, verticalalignment='bottom', horizontalalignment='left')


    def differential_capacity(self, subplot_ax, dQdV_no_nan, positive_peaks, negative_peaks=None):
        """Plot the differential capacity plot.

        Args:
            subplot_ax (matplotlib.axes): axis to which the plot should be added
            dQdV_no_nan (list): list of differential capacity
            positive_peaks (list): list of positive peaks
            negative_peaks (list): list of negative peaks
        """
        log.info("Creating differential capacity plot")
        subplot_ax.plot(self.voltage, dQdV_no_nan, linewidth=2, color="#425a81")
        # PLot the positive peaks as upper triangles
        for i in positive_peaks:
            subplot_ax.scatter(i, positive_peaks[i], marker='^', color='red', s=30)
        if negative_peaks:
            # PLot the negative peaks as lower triangles
            for i in negative_peaks:
                subplot_ax.scatter(i, negative_peaks[i], marker='v', color='red', s=30)

        if self.mass_of_active_material is not None:
            y_label = "Differential Capacity (mAh/g/V)"
        elif self.electrode_area is not None:
            y_label = "Differential Capacity (mAh/cm^2/V)"
        else:
            y_label = "Differential Capacity (mAh/V)"

        self.plot_identity(subplot_ax, xlabel="Voltage (V)", ylabel=y_label,
                            ax_sci_notation="y", x_lim=[min(self.voltage), max(self.voltage)], y_lim=[min(dQdV_no_nan), max(dQdV_no_nan)*1.1])


    def CP(self, subplot_ax, y_lim_min=0, y_lim_max=0):
        """Plot the voltage plot.

        Args:
            subplot_ax (matplotlib.axes): axis to which the plot should be added
            y_lim_min (float): minimum value of the y axis
        """
        log.info("Creating voltage plot")
        if self.procedure_type == "Voltammetry_CP":
            subplot_ax.scatter(self.time, self.voltage, s=2, label=f"{np.abs(np.mean(self.current)):.2e} A", color="#482b68")
        elif self.procedure_type == "Voltammetry_CA":
            subplot_ax.scatter(self.time, self.voltage, s=2, color="#482b68")
        if y_lim_min == "auto":
            y_lim_min = min(self.voltage)
        else:
            y_lim_min = min(self.voltage)*0.6
        if y_lim_max == "auto":
            y_lim_max = max(self.voltage)
        else:
            y_lim_max = max(self.voltage)*1.1
        self.plot_identity(subplot_ax, xlabel="Time (s)", ylabel="Voltage (V)",
                            ax_sci_notation="x", x_lim=[0, max(self.time)], y_lim=[y_lim_min, y_lim_max])
        subplot_ax.legend(loc="upper right")


    def potential_waveform(self, subplot_ax, data):
        """Plot the potential waveform plot.

        Args:
            subplot_ax (matplotlib.axes): axis to which the plot should be added
            data (pandas.DataFrame): dataframe of the data
        """
        # normalize the time for each cycle
        data_forward = data[data["scan_direction"] == "F"]
        data_backward = data[data["scan_direction"] == "B"]

        # check if the subplot_ax is part of a GridSpec layout
        if hasattr(subplot_ax, "get_subplotspec"):
            subplot_spec = subplot_ax.get_subplotspec()
        gs = gridspec.GridSpecFromSubplotSpec(2, 1, subplot_spec=subplot_spec, hspace=0.2)
        # create a subplot with 2 rows and 1 column with subplot_ax as the first subplot
        ax_1 = subplot_ax.figure.add_subplot(gs[0, 0])
        ax_1.plot(data_forward["time"], data_forward["voltage"], linewidth=0.9, color="#4b3b75")
        # make the x_axis to have scientific notation if it is more than 4 orders of magnitude
        self.plot_identity(ax_1, xlabel="Time (s)", ylabel=r"$V_{Anodic}$"+"(V)",
                           y_lim=[min(data_forward["voltage"]), max(data_forward["voltage"])],
                           ax_sci_notation = "x" if max(data_forward["time"]) > 1e3 else None)
        # put the y ticks for every 2 ticks
        ax_1.set_yticks(ax_1.get_yticks()[::2])
        ax_2 = subplot_ax.figure.add_subplot(gs[1, 0])
        ax_2.plot(data_backward["time"], data_backward["voltage"], linewidth=0.9, color="#9ac64d")
        self.plot_identity(ax_2, xlabel="Time (s)", ylabel=r"$V_{Cathodic}$"+"(V)",
                            y_lim=[min(data_backward["voltage"]), max(data_backward["voltage"])],
                            ax_sci_notation = "x" if max(data_backward["time"]) > 1e3 else None)
        # put the y ticks for every 2 ticks
        ax_2.set_yticks(ax_2.get_yticks()[::2])
        # remove the x ticks from the first subplot
        subplot_ax.axis('off')


    def CV(self, subplot_ax, data, anodic_peak_params, cathodic_peak_params, cycle_list):
        """Plot the CV plot.

        Args:
            subplot_ax (matplotlib.axes): axis to which the plot should be added
            data (pandas.DataFrame): dataframe of the data
            anodic_peak_params (dict): dictionary of anodic peak parameters
            cathodic_peak_params (dict): dictionary of cathodic peak parameters
        """
        # self.anodic_peak_params[cycle][peak_anodic_number]["capacitative_end_point"]
        # TODO: add height
        log.info("Creating CV plot")
        # increase the width size of the axis
        current_width, current_height = subplot_ax.get_figure().get_size_inches()
        new_width = current_width * 1.2
        subplot_ax.get_figure().set_size_inches(new_width, current_height)

        if cycle_list is None:
            cycle_list = data["cycle_number"].unique()
        # Array of colors from viridis with length of the number of cycles
        if len(cycle_list) < 10:
            # Take the first 10 colors from tab10 colormap
            colors = plt.get_cmap("tab10").colors
            tab10_colors = [colors[i] for i in range(10)]
            complementary_colors = [utils.get_complementary_color(color) for color in tab10_colors]
        else:
            colors = plt.cm.winter(np.linspace(0, 1, len(cycle_list)))
        # Loop through cycle with the plotted_cycle_frequency
        for cycle_num in cycle_list:
            # check if data['scan_rate'] is not None
            if not data['scan_rate'].isnull().values.any():
                label_name = f"Cyc. {cycle_num}@"+r"$\nu $"+"="+f"{data['scan_rate'][data['cycle_number']==cycle_num].mean() :.1f} V/s"
            else:
                label_name = f"Cyc. {cycle_num}"
            subplot_ax.plot(data[data["cycle_number"] == cycle_num]["voltage"], data[data["cycle_number"] == cycle_num]["current"],\
                            linewidth=0.9, color=colors[cycle_num-1], label=label_name)

            cycle = f"cycle_{cycle_num}"
            for peak in anodic_peak_params[cycle]:
                # check if the capacitative_start_point exists
                if "capacitative_start_point" in anodic_peak_params[cycle][peak]:
                    subplot_ax.plot([anodic_peak_params[cycle][peak]["voltage"],
                                    anodic_peak_params[cycle][peak]["voltage"]],
                                    [anodic_peak_params[cycle][peak]["current"],
                                    anodic_peak_params[cycle][peak]["capacitative_line"][0]*anodic_peak_params[cycle][peak]["voltage"]+\
                                    anodic_peak_params[cycle][peak]["capacitative_line"][1]],
                                    linestyle='--',  linewidth=0.3, color=complementary_colors[cycle_num-1], label=r"$h_{pa}, h_{pc}$")

                    subplot_ax.plot([anodic_peak_params[cycle][peak]["capacitative_start_point"]["voltage"],
                                    anodic_peak_params[cycle][peak]["voltage"]],
                                    [anodic_peak_params[cycle][peak]["capacitative_start_point"]["current"],
                                    anodic_peak_params[cycle][peak]["capacitative_line"][0]*anodic_peak_params[cycle][peak]["voltage"]+\
                                    anodic_peak_params[cycle][peak]["capacitative_line"][1]],
                                    linestyle=':', linewidth=0.5, color=colors[cycle_num-1], alpha=0.7)



            for peak in cathodic_peak_params[cycle]:

                if "capacitative_start_point" in cathodic_peak_params[cycle][peak]:
                    subplot_ax.plot([cathodic_peak_params[cycle][peak]["voltage"],
                                    cathodic_peak_params[cycle][peak]["voltage"]],
                                    [cathodic_peak_params[cycle][peak]["capacitative_line"][0]*cathodic_peak_params[cycle][peak]["voltage"]+\
                                    cathodic_peak_params[cycle][peak]["capacitative_line"][1],
                                    cathodic_peak_params[cycle][peak]["current"]],
                                    linestyle='--',  linewidth=0.3, color=complementary_colors[cycle_num-1])#,label=r"$h_{pa}, h_{pc}$"

                    subplot_ax.plot([cathodic_peak_params[cycle][peak]["capacitative_start_point"]["voltage"],
                                    cathodic_peak_params[cycle][peak]["voltage"]],
                                    [cathodic_peak_params[cycle][peak]["capacitative_start_point"]["current"],
                                    cathodic_peak_params[cycle][peak]["capacitative_line"][0]*cathodic_peak_params[cycle][peak]["voltage"]+\
                                    cathodic_peak_params[cycle][peak]["capacitative_line"][1]],
                                    linestyle=':',  linewidth=0.5, color=colors[cycle_num-1], alpha=0.7)




        self.plot_identity(subplot_ax, xlabel="Voltage (V)", ylabel="Current (A)",
                            x_lim=[min(data["voltage"]), max(data["voltage"])],
                            y_lim=[min(data["current"]), max(data["current"])])

        self._cv_legend(subplot_ax)


    def Tafel(self, subplot_ax, data, anodic_peak_params, cathodic_peak_params, E_half_params, cycle_list):
        """Plot the Tafel plot.

        Args:
            subplot_ax (matplotlib.axes): axis to which the plot should be added
            data (pandas.DataFrame): dataframe of the data
            anodic_peak_params (dict): dictionary of anodic peak parameters
            cathodic_peak_params (dict): dictionary of cathodic peak parameters
        """
        log.info("Creating Tafel plot")

        # Set a bigger size for the subplot due to the legend#
        current_width, current_height = subplot_ax.get_figure().get_size_inches()
        new_width = current_width * 1.2
        subplot_ax.get_figure().set_size_inches(new_width, current_height)

        if cycle_list is None:
            cycle_list = [i+1 for i in range(len(data))]

        # Array of colors from viridis with length of the number of cycles
        if len(cycle_list) < 10:
            # Take the first 10 colors from tab10 colormap
            colors = plt.get_cmap("tab10").colors
            tab10_colors = [colors[i] for i in range(10)]
            complementary_colors = [utils.get_complementary_color(color) for color in tab10_colors]
        else:
            colors = plt.cm.winter(np.linspace(0, 1, len(cycle_list)))

        # Loop through cycle with the plotted_cycle_frequency
        for cycle_number in cycle_list:
            for peak in E_half_params[f"cycle_{cycle_number}"].keys():
                peak_num = peak.split("pair_")[-1]
                # anodic tafel plot
                subplot_ax.plot(data[f"cycle_{cycle_number}"][peak]["anodic"]["voltage"],
                                np.log10(abs(data[f"cycle_{cycle_number}"][peak]["anodic"]["current"])),
                                linewidth=0.9, color=colors[cycle_number-1], label=f"Cyc. {cycle_number}")
                # anodic_tafel_line
                subplot_ax.plot([anodic_peak_params[f"cycle_{cycle_number}"][peak_num]["faradaic_start_point"]["voltage"],
                                E_half_params[f"cycle_{cycle_number}"][peak]["corrosion_point"]["voltage"]],
                                [anodic_peak_params[f"cycle_{cycle_number}"][peak_num]["faradaic_start_point"]["log_current"],
                                E_half_params[f"cycle_{cycle_number}"][peak]["corrosion_point"]["log_current"]],
                                linestyle=':', linewidth=0.5, color=colors[cycle_number-1], alpha=0.7, zorder=5)

                # cathodic tafel plot
                subplot_ax.plot(data[f"cycle_{cycle_number}"][peak]["cathodic"]["voltage"],
                                np.log10(abs(data[f"cycle_{cycle_number}"][peak]["cathodic"]["current"])),
                                linewidth=0.9, color=complementary_colors[cycle_number-1], label=f"Cyc. {cycle_number}")
                # cathodic_tafel_line
                subplot_ax.plot([cathodic_peak_params[f"cycle_{cycle_number}"][peak_num]["faradaic_start_point"]["voltage"],
                                E_half_params[f"cycle_{cycle_number}"][peak]["corrosion_point"]["voltage"]],
                                [cathodic_peak_params[f"cycle_{cycle_number}"][peak_num]["faradaic_start_point"]["log_current"],
                                E_half_params[f"cycle_{cycle_number}"][peak]["corrosion_point"]["log_current"]],
                                linestyle=':', linewidth=0.5, color=complementary_colors[cycle_number-1], alpha=0.7, zorder=5)
                # the corrosion  vertical line
                subplot_ax.axvline(x=E_half_params[f"cycle_{cycle_number}"][peak]["corrosion_point"]["voltage"],
                                   color="blue", linestyle='--', linewidth=0.5, alpha=0.7)

                subplot_ax.plot(E_half_params[f"cycle_{cycle_number}"][peak]["corrosion_point"]["voltage"],
                                E_half_params[f"cycle_{cycle_number}"][peak]["corrosion_point"]["log_current"],
                                "ro", label="Corrosion", markersize=1)

        self.plot_identity(subplot_ax, xlabel="Voltage (V)", ylabel="Log(Current) (Log(A))")
        # Add the legend outside the plot
        # Check if the legend has mulitple entries of "Corrosion point" and delete all except the last one
        # Retrieve current legend handles and labels
        handles, labels = subplot_ax.get_legend_handles_labels()

        # Process handles and labels
        new_labels = []
        new_handles = []
        cycle_handles = {}

        for handle, label in zip(handles, labels):
            if "Cyc." in label:
                if label not in cycle_handles:
                    cycle_handles[label] = [handle]
                else:
                    cycle_handles[label].append(handle)
            elif "Corrosion" == label:
                corrosion_point_handle = handle  # Keep the last handle

        # Grouping cycle handles
        for label, handle_group in cycle_handles.items():
            new_labels.append(label)
            new_handles.append(tuple(handle_group))

        # Adding corrosion point
        new_labels.append("Corrosion")
        new_handles.append(corrosion_point_handle)  # Add as a tuple if you want it to be treated the same as cycles

        # Creating custom legend
        subplot_ax.legend(new_handles, new_labels, handler_map={tuple: HandlerTuple(ndivide=None)}, loc='upper left', bbox_to_anchor=(1.05, 1))


    def peak_scan(self, subplot_ax, anodic_peak_params, cathodic_peak_params, E_half_params):
        """Plot the peak scan plot.

        Args:
            subplot_ax (matplotlib.axes): axis to which the plot should be added
            data (pandas.DataFrame): dataframe of the data
            scan_rate (float): scan rate
            anodic_peak_params (dict): dictionary of anodic peak parameters
            cathodic_peak_params (dict): dictionary of cathodic peak parameters
        """
        log.info("Creating peak scan plot")

        # Initialize lists to hold the data
        data = {"current_anodic": [], "current_cathodic": [], "voltage_anodic": [], "voltage_cathodic": [], "scan_rate": [],
                  "voltage_half": [], "peak_to_peak_seperation": []}

        for cycle, peak_pair_data in E_half_params.items():
            for _, pair_data in peak_pair_data.items():
                anodic_peak, cathodic_peak = pair_data['anodic_peak'], pair_data['cathodic_peak']

                data["current_anodic"].append(anodic_peak_params[cycle][anodic_peak]['current'])
                data["current_cathodic"].append(cathodic_peak_params[cycle][cathodic_peak]['current'])
                data["voltage_anodic"].append(anodic_peak_params[cycle][anodic_peak]['voltage'] - pair_data['E_half'])
                data["voltage_cathodic"].append(cathodic_peak_params[cycle][cathodic_peak]['voltage'] - pair_data['E_half'])
                data["scan_rate"].append(anodic_peak_params[cycle][anodic_peak]['scan_rate'])
                data["voltage_half"].append(pair_data['E_half'])
                data["peak_to_peak_seperation"].append(pair_data['peak_to_peak_seperation'])

        # Order data varaiable by scan rate (low to high)
        sorted_indices = sorted(range(len(data['scan_rate'])), key=lambda i: data['scan_rate'][i])
        data = {key: [value[i] for i in sorted_indices] for key, value in data.items()}

        # Create four subplots with shared x axis in the ax
        # check if the subplot_ax is part of a GridSpec layout
        if hasattr(subplot_ax, "get_subplotspec"):
            subplot_spec = subplot_ax.get_subplotspec()
        gs = gridspec.GridSpecFromSubplotSpec(4, 1, subplot_spec=subplot_spec, hspace=0)
        # Share the x axis
        ax_1 = subplot_ax.figure.add_subplot(gs[0, 0])
        # scan rate vs peak currents
        ax_1.scatter(data["scan_rate"], data["current_anodic"], color="#4b3b75", label="Anodic")
        ax_1.plot(data["scan_rate"], data["current_anodic"], linewidth=0.9, color="#4b3b75")
        ax_1.scatter(data["scan_rate"], data["current_cathodic"], color="#9ac64d", label="Cathodic")
        ax_1.plot(data["scan_rate"], data["current_cathodic"], linewidth=0.9, color="#9ac64d")
        self.plot_identity(ax_1, ylabel=r"$I_{p} (A)$", y_lim=[min(data["current_cathodic"])*1.5,\
                           max(data["current_anodic"])*1.5], y_label_fontsize=6)

        ax_2 = subplot_ax.figure.add_subplot(gs[1, 0], sharex=ax_1)
        ax_2.scatter(data["scan_rate"], data["voltage_anodic"], color="#4b3b75", label="Anodic")
        ax_2.plot(data["scan_rate"], data["voltage_anodic"], linewidth=0.9, color="#4b3b75")

        ax_2.scatter(data["scan_rate"], data["voltage_cathodic"], color="#9ac64d", label="Cathodic")
        ax_2.plot(data["scan_rate"], data["voltage_cathodic"], linewidth=0.9, color="#9ac64d")
        self.plot_identity(ax_2, ylabel=r"$E_{op} (V)$", y_lim=[min(data["voltage_cathodic"])*2,\
                            max(data["voltage_anodic"])*2], y_label_fontsize=6)
        # scan rate vs peak to peak seperation
        ax_3 = subplot_ax.figure.add_subplot(gs[2, 0], sharex=ax_1)
        ax_3.scatter(data["scan_rate"], data["peak_to_peak_seperation"], color="#3b9f7a")
        ax_3.plot(data["scan_rate"], data["peak_to_peak_seperation"], linewidth=0.9, color="#3b9f7a")
        self.plot_identity(ax_3, ylabel=r"$E_{p2p} (V)$", y_lim=[min(data["peak_to_peak_seperation"])*0.8,\
                            max(data["peak_to_peak_seperation"])*1.2], y_label_fontsize=6)

        # scan rate vs half voltage
        ax_4 = subplot_ax.figure.add_subplot(gs[3, 0], sharex=ax_1)
        ax_4.scatter(data["scan_rate"], data["voltage_half"], color="#3b9f7a")
        ax_4.plot(data["scan_rate"], data["voltage_half"], linewidth=0.9, color="#3b9f7a")
        self.plot_identity(ax_4, xlabel="Scan rate (V/s)", ylabel=r"$E_{1/2} (V)$", y_lim=[min(data["voltage_half"])*0.8,\
                            max(data["voltage_half"])*1.2], y_label_fontsize=6)
        for ax in [ax_1, ax_2, ax_3, ax_4]:
            # set the second and second to last y ticks
            len_y_ticks = len(ax.get_yticks())
            ax.set_yticks([ax.get_yticks()[1], ax.get_yticks()[len_y_ticks//2] ,ax.get_yticks()[-2]])
            ax.get_yaxis().set_label_coords(-0.13,0.5)
        ax_1.legend(loc="upper center", ncol=2, bbox_to_anchor=(0.5, 1.45), fontsize=7)
        subplot_ax.axis('off')


    def _charge_conversion(self):
        """Convert the charge to the correct units."""
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
