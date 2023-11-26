import os
import numpy as np

import scipy.constants as const
from scipy.signal import savgol_filter, find_peaks

import ruptures as rpt

from madap.utils import utils
from madap.echem.voltammetry.voltammetry import Voltammetry
from madap.echem.procedure import EChemProcedure
from madap.logger import logger

from madap.echem.voltammetry.voltammetry_CP_plotting import VoltammetryCPPlotting as cpplt

log = logger.get_logger("cyclic_potentiometry")


class Voltammetry_CP(Voltammetry, EChemProcedure):
    def __init__(self, voltage, current, time,  args, charge:list[float]=None) -> None:
        super().__init__(voltage, current, time, charge, args)
        self.applied_current = float(args.applied_current) if args.applied_current is not None else None # Unit: A
        self.dQdV = None # Unit: C/V
        self.dQdV_smoothed = None # Unit: C/V
        self.dVdt = None # Unit: V/h
        self.dVdt_smoothed = None # Unit: V/h
        self.tao_initial = None # Unit: s
        self.stabilization_transitions = {} # transition time (s): transition voltage (V)
        self.transition_times = {}
        self.d_coefficient = None # Unit: cm^2/s
        self.window_length = int(args.window_length) if args.window_length is not None else 51
        self.polyorder = int(args.polyorder) if args.polyorder is not None else 3

        self.positive_peaks = {}
        self.negative_peaks = {}

    def analyze(self):
        # Calculate: dQ/dV, dV/dt, initial stabilization time, potential transition time(s), diffusion coefficient,
        self._calculate_dQdV()
        self._calculate_dVdt()
        self._calculate_initial_stabilization_time()
        self._find_potential_transition_times()
        self._calculate_diffusion_coefficient()

    def plot(self, save_dir, plots, optional_name: str = None):
        plot_dir = utils.create_dir(os.path.join(save_dir, "plots"))
        plot = cpplt(self.current, self.time, self.voltage, self.applied_current,
                     self.electrode_area, self.mass_of_active_material, self.cumulative_charge)
        # "CP", "CC", "Cottrell", "Voltage_Profile", "Potential_Rate", "Differential_Capacity"
        fig, available_axes = plot.compose_ca_subplot(plots=plots)
        for sub_ax, plot_name in zip(available_axes, plots):
            if plot_name == "CP":
                plot.CP(subplot_ax=sub_ax)
            elif plot_name == "CC":
                plot.CC(subplot_ax=sub_ax)
            elif plot_name == "Cottrell":
                plot.Cottrell(subplot_ax=sub_ax, diffusion_coefficient=self.d_coefficient)
            elif plot_name == "Voltage_Profile":
                plot.Voltage_Profile(subplot_ax=sub_ax)
            elif plot_name == "Potential_Rate":
                plot.Potential_Rate(subplot_ax=sub_ax)
            elif plot_name == "Differential_Capacity":
                plot.Differential_Capacity(subplot_ax=sub_ax)
            else:
                log.error("Voltammetry CP class does not have the selected plot.")
                continue

        fig.tight_layout()
        self.figure = fig
        name = utils.assemble_file_name(optional_name, self.__class__.__name__) if \
                    optional_name else utils.assemble_file_name(self.__class__.__name__)
        plot.save_plot(fig, plot_dir, name)

    def save_data(self):
        pass

    def perform_all_actions(self, save_dir:str, plots:list, optional_name:str = None):
        self.analyze()
        self.plot(save_dir, plots, optional_name=optional_name)
        self.save_data(save_dir=save_dir, optional_name=optional_name)


    def _impute_mean_nearest_neighbors(self, data):
        """Impute NaN values using the mean of nearest neighbors."""
        n = len(data)
        for i in range(n):
            if np.isnan(data[i]):
                left = right = i
                # Move left index to the nearest non-NaN value
                while left >= 0 and np.isnan(data[left]):
                    left -= 1
                # Move right index to the nearest non-NaN value
                while right < n and np.isnan(data[right]):
                    right += 1

                # Compute mean of nearest non-NaN neighbors
                neighbors = []
                if left >= 0:
                    neighbors.append(data[left])
                if right < n:
                    neighbors.append(data[right])

                data[i] = np.mean(neighbors) if neighbors else 0
        return data

    def _calculate_dQdV(self):
        # Convert the cumulative charge from As to mAh
        cumulative_charge_mAh = self.np_cumulative_charge * (1000/3600)

        # Calculate the differential of charge with respect to voltage
        dQdV = np.gradient(cumulative_charge_mAh, self.np_voltage)  # mAh/V
        # Impute NaN values in dQdV and smooth the data using Savitzky-Golay filter
        dQdV_no_nan = self._impute_mean_nearest_neighbors(dQdV)
        self.dQdV_smoothed = savgol_filter(dQdV_no_nan, self.window_length, self.polyorder)
        # If mass is available, convert it to mAh/gV
        if self.mass_of_active_material is not None:
            dQdV_no_nan /= self.mass_of_active_material  # mAh/gV

        # Peak detection for smoothed dQ/dV data
        positive_peaks_indices, _ = find_peaks(self.dQdV_smoothed)
        negative_peaks_indices, _ = find_peaks(-self.dQdV_smoothed)  # Invert the curve to find negative peaks

        # Store the indices and values of the peaks
        self.positive_peaks = {self.np_voltage[i]: self.dQdV_smoothed[i] for i in positive_peaks_indices}
        self.negative_peaks = {self.np_voltage[i]: self.dQdV_smoothed[i] for i in negative_peaks_indices}

        self.dQdV = dQdV_no_nan

    def _calculate_dVdt(self):
        self.dVdt = np.gradient(self.np_voltage, self.np_time) * 3600  # V/h

    def _calculate_initial_stabilization_time(self):

        model = "l1"  # L1 norm minimization
        algo = rpt.Pelt(model=model).fit(self.np_voltage)
        result = algo.predict(pen=10)  # Adjust pen value as needed

        # The first change point is the end of the initial stabilization phase
        self.tao_initial = self.np_time[result[0]] if result else None
        self.stabilization_transitions[self.tao_initial] = self.np_voltage[result[0]] if result else None


    def _find_potential_transition_times(self, window_length=51, polyorder=3):
        """Find potential transition times and their corresponding transition voltages.
        This functions excludes the initial stabilization time.
        """
        # Apply Savitzky-Golay filter to smooth dV/dt data
        self.dVdt_smoothed = savgol_filter(self.dVdt, window_length, polyorder)

        # Calculate second derivative of the smoothed dV/dt data
        d2Vdt2 = np.gradient(self.dVdt_smoothed, self.np_time)

        # Threshold for identifying significant changes
        threshold = np.std(d2Vdt2) * 3

        # Find indices where the second derivative exceeds the threshold
        transition_indices = np.where(np.abs(d2Vdt2) > threshold)[0]

        # Filter out times within the initial stabilization phase
        transition_indices = transition_indices[self.np_time[transition_indices] > self.tao_initial]
        self.transition_times = {self.np_time[i]: self.np_voltage[i] for i in transition_indices}

    def _calculate_diffusion_coefficient(self):
        """Calculate the diffusion coefficient value using Sand's formula without tau.
        """
        # Assume that I (current) is known
        # Note: Ensure that the values of n, F, A, and c are provided correctly
        faraday_constant = const.physical_constants["Faraday constant"][0]
        # Calculate the coefficient part of the diffusion coefficient using Sand's formula without tau
        # Coefficient = (4 * I^2) / ((n * F * A * c)^2 * pi)
        if self.applied_current is not None:
            current = self.applied_current
        else:
            current = np.mean(self.np_current)
        self.d_coefficient = (4 * current**2) / ((self.number_of_electrons * faraday_constant * self.electrode_area * self.concentration_of_active_material)**2 * np.pi)

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