"""This module contains the Voltammetry class, which is used to analyze voltammetry data."""

import os

import numpy as np
import scipy.constants as const
from scipy.stats import linregress

from madap.echem.procedure import EChemProcedure
from madap.logger import logger
from madap.utils import utils

log = logger.get_logger("voltammetry")


class Voltammetry(EChemProcedure):
    """This class defines the voltammetry method."""

    def __init__(self, voltage, current, time, args, charge=None) -> None:
        """Initialize the voltammetry method.
        Args:
            voltage (list): list of voltages
            current (list): list of currents
            time (list): list of times
            charge (list): list of charges
            args (argparse.Namespace): arguments
        """
        self.figure = None
        self.faraday_constant = const.physical_constants["Faraday constant"][
            0
        ]  # Unit: C/mol
        # gas constant
        self.gas_constant = const.physical_constants["molar gas constant"][
            0
        ]  # Unit: J/mol/K
        self.voltage = voltage
        self.np_voltage = np.array(voltage)  # Unit: V

        self.current = current
        self.np_current = np.array(self.current)  # Unit: A

        self.time = time
        self.np_time = np.array(self.time) if self.time else None  # Unit: s

        if self.np_time is not None:
            self.cumulative_charge = (
                self._calculate_charge() if charge is None else charge
            )
            self.np_cumulative_charge = np.array(self.cumulative_charge)  # Unit: C
            self.convert_time()
        else:
            self.cumulative_charge = None
            self.np_cumulative_charge = None


        self.mass_of_active_material = (
            float(args.mass_of_active_material)
            if args.mass_of_active_material is not None
            else None
        )  # Unit: g
        self.electrode_area = (
            float(args.electrode_area) if args.electrode_area is not None else 1
        )  # Unit: cm^2
        self.concentration_of_active_material = (
            float(args.concentration_of_active_material)
            if args.concentration_of_active_material is not None
            else 1
        )  # Unit: mol/cm^3

        self.window_size = (
            int(args.window_size)
            if args.window_size is not None
            else len(self.np_time) - 1
        )

        self.measured_current_unit = args.measured_current_units
        self.measured_time_unitis = args.measured_time_units
        self.number_of_electrons = int(args.number_of_electrons)

        self.convert_current()


    def save_figure(self, fig, plot, optional_name=None, plot_dir=None):
        """Save the figure in the plot directory.

        Args:
            fig (matplotlib.figure.Figure): figure to save
            plot (madap.plot.plot): plot object
            optional_name (str): optional name for the figure
            plot_dir (str): plot directory
        """
        fig.tight_layout()
        self.figure = fig
        name = (
            utils.assemble_file_name(optional_name, self.__class__.__name__)
            if optional_name
            else utils.assemble_file_name(self.__class__.__name__)
        )
        plot.save_plot(fig, plot_dir, name)

    def _save_data_with_name(self, optional_name, class_name, save_dir, data):
        """Save the data in the save directory.

        Args:
            optional_name (str): optional name for the data
            class_name (str): class name
            save_dir (str): save directory
            data (pd.DataFrame): data to save
        """
        data_name = (
            utils.assemble_file_name(optional_name, class_name, "data.csv")
            if optional_name
            else utils.assemble_file_name(class_name, "data.csv")
        )
        utils.save_data_as_csv(save_dir, data, data_name)

    def _assemble_name(self, save_dir, optional_name, class_name):
        """Assemble the name of the file.

        Args:
            save_dir (str): save directory
            optional_name (str): optional name for the file
            class_name (str): class name
        """
        save_dir = utils.create_dir(os.path.join(save_dir, "data"))

        name = (
            utils.assemble_file_name(optional_name, class_name, "params.json")
            if optional_name
            else utils.assemble_file_name(class_name, "params.json")
        )
        return save_dir, name

    def convert_current(self):
        """Convert the current to A indipendently from the unit of measure"""
        if self.measured_current_unit == "uA":
            self.current = self.current * 1e-6
        elif self.measured_current_unit == "mA":
            self.current = self.current * 1e-3
        elif self.measured_current_unit == "A":
            self.current = self.current * 1e0
        else:
            log.error("Current unit not supported. Supported units are: uA, mA, A")
            raise ValueError("Current unit not supported")

    def convert_time(self):
        """Convert the time to s indipendently from the unit of measure"""
        if self.measured_time_unitis == "s":
            self.time = self.time * 1e0
        elif self.measured_time_unitis == "min":
            self.time = self.time * 60
        elif self.measured_time_unitis == "h":
            self.time = self.time * 3600
        elif self.measured_time_unitis == "ms":
            self.time = self.time * 1e-3
        else:
            log.error("Time unit not supported. Supported units are: s, min, h")
            raise ValueError("Time unit not supported")

    def analyze_best_linear_fit(self, x_data, y_data):
        """
        Find the best linear region for the provided data.

        Args:
            x_data (np.array): Transformed time array (e.g., t^(-1/2) for diffusion or time for kinetics).
            y_data (np.array): Current array or transformed current array (e.g., log(current)).

        Returns:
            best fit (dict): Dictionary containing the best linear fit parameters:
                start_index (int): Start index of the best linear region.
                end_index (int): End index of the best linear region.
                slope (float): Slope of the best linear fit.
                intercept (float): Intercept of the best linear fit.
                r_squared (float): R-squared value of the best linear fit.
        """

        best_fit = {
            "start": 0,
            "end": self.window_size,
            "r_squared": 0,
            "slope": 0,
            "intercept": 0,
        }
        for start in range(len(x_data) - self.window_size + 1):
            end = start + self.window_size
            slope, intercept, r_value, _, _ = linregress(
                x_data[start:end], y_data[start:end]
            )
            r_squared = r_value**2
            if r_squared > best_fit["r_squared"]:
                best_fit.update(
                    {
                        "start": start,
                        "end": end,
                        "r_squared": r_squared,
                        "slope": slope,
                        "intercept": intercept,
                    }
                )
        log.info(
            f"Best linear fit found from {best_fit['start']} to {best_fit['end']} with R^2 = {best_fit['r_squared']}"
        )
        return best_fit

    def _calculate_charge(self):
        """Calculate the cumulative charge passed in a voltammetry experiment."""
        # Calculate the time intervals (delta t)
        delta_t = np.diff(self.np_time)

        # Calculate the charge for each interval as the product of the interval duration and the current at the end of the interval
        interval_charges = delta_t * self.np_current[1:]

        # Compute the cumulative charge
        return np.cumsum(np.insert(interval_charges, 0, 0)).tolist()
