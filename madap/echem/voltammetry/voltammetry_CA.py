""" This module defines the cyclic amperometry methods. It is a subclass of the Voltammetry class  and the EChemProcedure class.
It contains the cyclic amperometry methods for analyzing the data and plotting the results."""
import os

import numpy as np

from madap.utils import utils
from madap.echem.voltammetry.voltammetry import Voltammetry
from madap.echem.procedure import EChemProcedure
from madap.logger import logger

from madap.echem.voltammetry.voltammetry_plotting import VoltammetryPlotting as voltPlot

log = logger.get_logger("cyclic_amperometry")


class Voltammetry_CA(Voltammetry, EChemProcedure):
    """ This class defines the chrono amperometry method."""
    def __init__(self, current, voltage, time, args, charge=None) -> None:
        super().__init__(voltage, current, time, args, charge=charge)
        self.applied_voltage = float(args.applied_voltage) if args.applied_voltage is not None else None # Unit: V
        self.diffusion_coefficient = None # Unit: cm^2/s
        self.reaction_order = None # 1 or 2
        self.reaction_rate_constant = None # Unit: 1/s or cm^3/mol/s
        self.best_fit_reaction_rate = None
        self.best_fit_diffusion = None

    def analyze(self):
        """ Analyze the data to calculate the diffusion coefficient and reaction rate constant:
        1. Calculate the diffusion coefficient using Cottrell analysis.
        2. Analyze the reaction kinetics to determine if the reaction is first or second order.
        """
        # Calculate diffusion coefficient
        self._calculate_diffusion_coefficient()

        # Reaction kinetics analysis
        self._analyze_reaction_kinetics()


    def _calculate_diffusion_coefficient(self):
        """ Calculate the diffusion coefficient using Cottrell analysis."""
        log.info("Calculating diffusion coefficient using Cottrell analysis...")
        # Find the best linear region for Cottrell analysis
        t_inv_sqrt = np.sqrt(1 / self.np_time[1:])  # Avoid division by zero
        best_fit = self.analyze_best_linear_fit(t_inv_sqrt, self.np_current[1:])
        slope = best_fit['slope']
        # Calculate D using the slope
        # Unit of D: cm^2/s
        # Cortrell equation: I = (nFAD^1/2 * C)/ (pi^1/2 * t^1/2)
        self.diffusion_coefficient = (slope ** 2 * np.pi) / (self.number_of_electrons ** 2 * \
                                                            self.faraday_constant ** 2 * \
                                                            self.electrode_area ** 2 * \
                                                            self.concentration_of_active_material ** 2)
        log.info(f"Diffusion coefficient: {self.diffusion_coefficient} cm^2/s")
        self.best_fit_diffusion = best_fit


    def _analyze_reaction_kinetics(self):
        """
        Analyze the reaction kinetics to determine if the reaction is zero, first or second order. Higher order reactions are not considered here.
        for the zero order, the rate low: I = I0 - kt
        for the first order, the rate low: ln(I) = ln(I0) - kt
        for the second order, the rate low: 1/I = 1/I0 + kt
        and calculate the rate constant accordingly.
        """
        # Analyze for zero-order kinetics
        log.info("Analyzing reaction kinetics for zero kinetic order...")
        zero_order_fit = self.analyze_best_linear_fit(x_data=self.np_time[1:], y_data=self.np_current[1:])
        # Analyze for first-order kinetics
        log.info("Analyzing reaction kinetics for first kinetic order...")
        first_order_fit = self.analyze_best_linear_fit(x_data=self.np_time[1:], y_data=np.log(self.np_current[1:]))
        # Analyze for second-order kinetics
        log.info("Analyzing reaction kinetics for second kinetic order...")
        second_order_fit = self.analyze_best_linear_fit( x_data=self.np_time[1:], y_data=1/self.np_current[1:])


        # Determine which order fits best
        if (zero_order_fit['r_squared'] > first_order_fit['r_squared']) and (zero_order_fit['r_squared'] > second_order_fit['r_squared']):
            log.info("The reaction is zero-order.")
            self.reaction_order = 0
            self.reaction_rate_constant = -zero_order_fit['slope']
            self.best_fit_reaction_rate = zero_order_fit
            log.info(f"Reaction rate constant for zero order: {self.reaction_rate_constant} A/s")
            log.info("A positive rate constant indicates a decay process, while a negative one indicates an increasing process or growth.")

        if first_order_fit['r_squared'] > second_order_fit['r_squared']:
            log.info("The reaction is first-order.")
            self.reaction_order = 1
            # Assigning the negative of the slope for first-order kinetics
            self.reaction_rate_constant = -first_order_fit['slope']
            self.best_fit_reaction_rate = first_order_fit
            log.info(f"Reaction rate constant for first order: {self.reaction_rate_constant} 1/s")
            log.info("A positive rate constant indicates a decay process, while a negative one indicates an increasing process or growth.")

        else:
            log.info("The reaction is second-order.")
            self.reaction_order = 2
            self.reaction_rate_constant = second_order_fit['slope']
            self.best_fit_reaction_rate = second_order_fit
            log.info(f"Reaction rate constant for second order: {self.reaction_rate_constant} cm^3/mol/s")
            log.info("A positive rate constant indicates a typical second-order increasing concentration process.")


    def plot(self, save_dir, plots, optional_name: str = None):
        """Plot the data.

        Args:
            save_dir (str): The directory where the plot should be saved.
            plots (list): A list of plots to be plotted.
            optional_name (str): The optional name of the plot.
        """
        plot_dir = utils.create_dir(os.path.join(save_dir, "plots"))
        plot = voltPlot(current=self.np_current, time=self.np_time,
                        voltage=self.voltage,
                        electrode_area=self.electrode_area,
                        mass_of_active_material=self.mass_of_active_material,
                        cumulative_charge=self.cumulative_charge,
                        procedure_type=self.__class__.__name__,
                        applied_voltage=self.applied_voltage)
        if self.voltage is None and "Voltage" in plots:
            log.warning("Measured voltage is not provided. Voltage plot is not available.")
            # Drop the voltage plot from the plots list
            plots = [plot for plot in plots if plot != "Voltage"]

        fig, available_axes = plot.compose_volt_subplot(plots=plots)
        for sub_ax, plot_name in zip(available_axes, plots):
            if plot_name == "CA":
                plot.CA(subplot_ax=sub_ax)
            elif plot_name == "Log_CA":
                if self.reaction_order == 0:
                    y_data = self.np_current[1:]
                elif self.reaction_order == 1:
                    y_data = np.log(self.np_current[1:])
                elif self.reaction_order == 2:
                    y_data = 1/self.np_current[1:]
                plot.log_CA(subplot_ax=sub_ax, y_data = y_data,
                            reaction_rate=self.reaction_rate_constant,
                            reaction_order=self.reaction_order,
                            best_fit_reaction_rate=self.best_fit_reaction_rate)
            elif plot_name == "CC":
                plot.CC(subplot_ax=sub_ax)
            elif plot_name == "Cottrell":
                plot.cottrell(subplot_ax=sub_ax, diffusion_coefficient=self.diffusion_coefficient, best_fit_diffusion=self.best_fit_diffusion)
            elif plot_name == "Anson":
                plot.anson(subplot_ax=sub_ax, diffusion_coefficient=self.diffusion_coefficient)
            elif plot_name == "Voltage":
                plot.CP(subplot_ax=sub_ax)
            else:
                log.error("Voltammetry CA class does not have the selected plot.")
                continue

        self.save_figure(fig, plot, optional_name=optional_name, plot_dir=plot_dir)

    def save_data(self, save_dir:str, optional_name:str = None):
        """Save the data

        Args:
            save_dir (str): The directory where the data should be saved
            optional_name (str): The optional name of the data.
        """
        log.info("Saving data...")
        # Create a directory for the data
        save_dir, name = self._assemble_name(save_dir, optional_name, self.__class__.__name__)
        if self.reaction_order == 0:
            reaction_rate_constant_unit = "A/s"
        elif self.reaction_order == 1:
            reaction_rate_constant_unit = "1/s"
        elif self.reaction_order == 2:
            reaction_rate_constant_unit = "cm^3/mol/s"
        # Add the settings and processed data to the dictionary
        added_data = {
            "Applied voltage [V]": self.applied_voltage,
            "Diffusion coefficient [cm^2/s]": self.diffusion_coefficient,
            "Reaction order": self.reaction_order,
            f"Reaction rate constant ({reaction_rate_constant_unit})": self.reaction_rate_constant,
            "Best fit reaction rate": self.best_fit_reaction_rate,
            "Best fit diffusion": self.best_fit_diffusion,
            "Electrode area [cm^2]": self.electrode_area,
            "Mass of active material [g]": self.mass_of_active_material,
            "Concentration of active material [mol/cm^3]": self.concentration_of_active_material,
            "Window size of fit": self.window_size
        }
        utils.save_data_as_json(save_dir, added_data, name)

        # Save the raw data
        data = utils.assemble_data_frame(**{
            "voltage [V]": self.voltage,
            "current [A]": self.current,
            "time [s]": self.time,
            "cumulative_charge [C]": self.cumulative_charge
        })

        self._save_data_with_name(optional_name, self.__class__.__name__, save_dir, data)


    def perform_all_actions(self, save_dir:str, plots:list, optional_name:str = None):
        """Perform all the actions for the cyclic amperometry method: analyze, plot, and save data."""

        self.analyze()
        self.plot(save_dir, plots, optional_name=optional_name)
        self.save_data(save_dir=save_dir, optional_name=optional_name)

    @property
    def figure(self):
        """Get the figure of the plot.

        Returns:
            obj: Figure object for ca plot.
        """
        return self._figure


    @figure.setter
    def figure(self, figure):
        """Set the figure of the plot.

        Args:
            figure (obj): Figure object for ca plot.
        """
        self._figure = figure
