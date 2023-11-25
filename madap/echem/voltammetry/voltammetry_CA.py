import os

import numpy as np

import scipy.constants as const

from madap.utils import utils
from madap.echem.voltammetry.voltammetry import Voltammetry
from madap.echem.procedure import EChemProcedure
from madap.logger import logger

from madap.echem.voltammetry.voltammetry_CA_plotting import VoltammetryCAPlotting as caplt

log = logger.get_logger("cyclic_amperometry")


class Voltammetry_CA(Voltammetry, EChemProcedure):
    """ This class defines the chrono amperometry method."""
    def __init__(self, current, voltage, time, args, charge:list[float]=None) -> None:
        super().__init__(voltage, current, time, args.measured_current_units, args.measured_time_units, args.number_of_electrons)
        self.voltage = voltage
        self.applied_voltage = float(args.applied_voltage) if args.applied_voltage is not None else None # Unit: V
        self.np_time = np.array(self.time) # Unit: s
        self.np_current = np.array(self.current) # Unit: A
        self.cumulative_charge = self._calculate_charge() if charge is None else charge # Unit: C
        self.mass_of_active_material = float(args.mass_of_active_material) if args.mass_of_active_material is not None else None # Unit: g
        self.electrode_area = float(args.electrode_area) if args.electrode_area is not None else 1 # Unit: cm^2
        self.concentration_of_active_material = float(args.concentration_of_active_material) if args.concentration_of_active_material is not None else 1 # Unit: mol/cm^3
        self.window_size = int(args.window_size) if args.window_size is not None else len(self.np_time)
        self.diffusion_coefficient = None # Unit: cm^2/s
        self.reaction_order = None # 1 or 2
        self.reaction_rate_constant = None # Unit: 1/s or cm^3/mol/s
        self.best_fit_reaction_rate = None
        self.best_fit_diffusion = None

    def analyze(self):
        # Calculate diffusion coefficient
        self._calculate_diffusion_coefficient()

        # Reaction kinetics analysis
        self._analyze_reaction_kinetics()


    def _calculate_charge(self):
        """ Calculate the cumulative charge passed in a chronoamperometry experiment."""
        # Calculate the time intervals (delta t)
        delta_t = np.diff(self.np_time)

        # Calculate the charge for each interval as the product of the interval duration and the current at the end of the interval
        interval_charges = delta_t * self.np_current[1:]

        # Compute the cumulative charge
        return np.cumsum(np.insert(interval_charges, 0, 0)).tolist()


    def _calculate_diffusion_coefficient(self):
        """ Calculate the diffusion coefficient using Cottrell analysis."""
        log.info("Calculating diffusion coefficient using Cottrell analysis...")
        # Find the best linear region for Cottrell analysis
        t_inv_sqrt = np.sqrt(1 / self.np_time[1:])  # Avoid division by zero
        best_fit = self.analyze_best_linear_fit(t_inv_sqrt, self.np_current[1:])
        slope = best_fit['slope']
        # Constants for Cottrell equation
        faraday_constant = const.physical_constants["Faraday constant"][0]  # Faraday constant in C/mol
        # Calculate D using the slope
        # Unit of D: cm^2/s
        # Cortrell equation: I = (nFAD^1/2 * C)/ (pi^1/2 * t^1/2)
        self.diffusion_coefficient = (slope ** 2 * np.pi) / (self.number_of_electrons ** 2 * faraday_constant ** 2 * self.electrode_area ** 2 * self.concentration_of_active_material ** 2)
        log.info(f"Diffusion coefficient: {self.diffusion_coefficient} cm^2/s")
        self.best_fit_diffusion = best_fit


    def _analyze_reaction_kinetics(self):
        """
        Analyze the reaction kinetics to determine if the reaction is first or second order.
        for the first order, the rate low: ln(I) = ln(I0) - kt
        for the second order, the rate low: 1/I = 1/I0 + kt
        and calculate the rate constant accordingly.
        """
        # Analyze for first-order kinetics
        log.info("Analyzing reaction kinetics for first kinetic order...")
        first_order_fit = self.analyze_best_linear_fit(x_data=self.np_time[1:], y_data=np.log(self.np_current[1:]))
        # Analyze for second-order kinetics
        log.info("Analyzing reaction kinetics for second kinetic order...")
        second_order_fit = self.analyze_best_linear_fit( x_data=self.np_time[1:], y_data=1/self.np_current[1:])


        # Determine which order fits best
        if first_order_fit['r_squared'] > second_order_fit['r_squared']:
            self.reaction_order = 1
            # Assigning the negative of the slope for first-order kinetics
            self.reaction_rate_constant = -first_order_fit['slope']
            self.best_fit_reaction_rate = first_order_fit
            log.info(f"Reaction rate constant for first order: {self.reaction_rate_constant} 1/s")
            log.info("A positive rate constant indicates a decay process, while a negative one indicates an increasing process or growth.")

        else:
            self.reaction_order = 2
            self.reaction_rate_constant = second_order_fit['slope']
            self.best_fit_reaction_rate = second_order_fit
            log.info(f"Reaction rate constant for second order: {self.reaction_rate_constant} cm^3/mol/s")
            log.info("A positive rate constant indicates a typical second-order increasing concentration process.")


    def plot(self, save_dir, plots, optional_name: str = None):
        plot_dir = utils.create_dir(os.path.join(save_dir, "plots"))
        plot = caplt(current=self.np_current, time=self.np_time,
                        voltage=self.voltage, applied_voltage=self.applied_voltage,
                        electrode_area=self.electrode_area,
                        mass_of_active_material=self.mass_of_active_material,
                        cumulative_charge=self.cumulative_charge)
        if self.voltage is None and "Voltage" in plots:
            log.warning("Measured voltage is not provided. Voltage plot is not available.")
            # Drop the voltage plot from the plots list
            plots = [plot for plot in plots if plot != "Voltage"]

        fig, available_axes = plot.compose_ca_subplot(plots=plots)
        for sub_ax, plot_name in zip(available_axes, plots):
            if plot_name == "CA":
                plot.CA(subplot_ax=sub_ax)
            elif plot_name == "Log_CA":
                if self.reaction_order == 1:
                    y_data = np.log(self.np_current[1:])
                elif self.reaction_order == 2:
                    y_data = 1/self.np_current[1:]
                plot.Log_CA(subplot_ax=sub_ax, y_data = y_data,
                            reaction_rate=self.reaction_rate_constant,
                            reaction_order=self.reaction_order,
                            best_fit_reaction_rate=self.best_fit_reaction_rate)
            elif plot_name == "CC":
                plot.CC(subplot_ax=sub_ax)
            elif plot_name == "Cottrell":
                plot.Cottrell(subplot_ax=sub_ax, diffusion_coefficient=self.diffusion_coefficient, best_fit_diffusion=self.best_fit_diffusion)
            elif plot_name == "Anson":
                plot.Anson(subplot_ax=sub_ax, diffusion_coefficient=self.diffusion_coefficient)
            elif plot_name == "Voltage":
                plot.Voltage(subplot_ax=sub_ax)
            else:
                log.error("Voltammetry CA class does not have the selected plot.")
                continue

        fig.tight_layout()
        self.figure = fig
        name = utils.assemble_file_name(optional_name, self.__class__.__name__) if \
                    optional_name else utils.assemble_file_name(self.__class__.__name__)
        plot.save_plot(fig, plot_dir, name)


    def save_data(self, save_dir:str, optional_name:str = None):
        """Save the data
        
        Args:
            save_dir (str): The directory where the data should be saved
            optional_name (str): The optional name of the data.
        """
        log.info("Saving data...")
        # Create a directory for the data
        save_dir = utils.create_dir(os.path.join(save_dir, "data"))
        
        name = utils.assemble_file_name(optional_name, self.__class__.__name__, "params.json") if \
                    optional_name else utils.assemble_file_name(self.__class__.__name__, "params.json")
        
        if self.reaction_order == 1:
            reaction_rate_constant_unit = "1/s"
        elif self.reaction_order == 2:
            reaction_rate_constant_unit = "cm^3/mol/s"
        # Add the settings and processed data to the dictionary
        added_data = {
            "Applied voltage [[V]": self.applied_voltage,
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
        data_name = utils.assemble_file_name(optional_name, self.__class__.__name__, "data.csv") if \
                    optional_name else utils.assemble_file_name(self.__class__.__name__, "data.csv")
        utils.save_data_as_csv(save_dir, data, data_name)

    def perform_all_actions(self, save_dir:str, plots:list, optional_name:str = None):
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