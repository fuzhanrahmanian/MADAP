"""This module contains the cyclic potentiometry class."""
import os
import numpy as np


from scipy.signal import savgol_filter, find_peaks
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

import ruptures as rpt

from madap.utils import utils
from madap.echem.voltammetry.voltammetry import Voltammetry
from madap.echem.procedure import EChemProcedure
from madap.logger import logger

from madap.echem.voltammetry.voltammetry_plotting import VoltammetryPlotting as voltPlot


log = logger.get_logger("cyclic_potentiometry")


class Voltammetry_CP(Voltammetry, EChemProcedure):
    """This class defines the cyclic potentiometry method."""
    def __init__(self, voltage, current, time,  args, charge:list[float]=None) -> None:
        super().__init__(voltage, current, time, args, charge=charge)
        self.applied_current = float(args.applied_current) if args.applied_current is not None else None # Unit: A
        self.dQdV = None # Unit: C/V
        self.dQdV_unit = None
        self.dVdt = None # Unit: V/h
        self.dVdt_smoothed = None # Unit: V/h
        self.tao_initial = None # Unit: s
        self.stabilization_values = {} # transition time (s): transition voltage (V)
        self.transition_values = {}
        self.d_coefficient = None # Unit: cm^2/s
        self.penalty_value = float(args.penalty_value) if args.penalty_value is not None else 0.25

        self.positive_peaks = {}
        self.negative_peaks = {}

    def analyze(self):
        """Analyze the cyclic potentiometry data. These analysis include:
        1. Calculate dQ/dV
        2. Calculate dV/dt
        3. Calculate initial stabilization time
        4. Find potential transition times
        5. Calculate diffusion coefficient
        """
        # Calculate: dQ/dV, dV/dt, initial stabilization time, potential transition time(s), diffusion coefficient,
        self._calculate_dQdV()
        self._calculate_dVdt()
        self._calculate_initial_stabilization_time()
        self._find_potential_transition_times()
        self._calculate_diffusion_coefficient()


    def plot(self, save_dir, plots, optional_name: str = None):
        plot_dir = utils.create_dir(os.path.join(save_dir, "plots"))
        plot = voltPlot(current=self.np_current, time=self.np_time,
                        voltage=self.np_voltage,
                        electrode_area=self.electrode_area,
                        mass_of_active_material=self.mass_of_active_material,
                        cumulative_charge=self.cumulative_charge,
                        procedure_type=self.__class__.__name__,
                        applied_current=self.applied_current)
        fig, available_axes = plot.compose_volt_subplot(plots=plots)
        for sub_ax, plot_name in zip(available_axes, plots):
            if plot_name == "CP":
                plot.CP(subplot_ax=sub_ax)
            elif plot_name == "CC":
                plot.CC(subplot_ax=sub_ax)
            elif plot_name == "Cottrell":
                plot.cottrell(subplot_ax=sub_ax, diffusion_coefficient=self.d_coefficient)
            elif plot_name == "Voltage_Profile":
                plot.voltage_profile(subplot_ax=sub_ax)
            elif plot_name == "Potential_Rate":
                plot.potential_rate(subplot_ax=sub_ax, dVdt=self.dVdt, transition_values=self.transition_values,
                                    tao_initial=self.tao_initial)
            elif plot_name == "Differential_Capacity":
                plot.differential_capacity(subplot_ax=sub_ax, dQdV_no_nan=self.dQdV,positive_peaks=self.positive_peaks,
                                            negative_peaks=self.negative_peaks)
            else:
                log.error("Voltammetry CP class does not have the selected plot.")
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
        # add the settings and processed data to the dictionary
        added_data = {
            "Applied Current [A]": self.applied_current,
            "Penalty Value": self.penalty_value,
            "Initial Stabilization Time [s]": self.tao_initial,
            "Stabilization Values {time [s]: potential [V]}": self.stabilization_values,
            "Transition Values {time [s]: potential [V]}": self.transition_values,
            "Diffusion Coefficient [cm^2/s]": f"{self.d_coefficient} * Tau",
            "Positive_peaks {potential [V]: dQdV" + f"{self.dQdV_unit}" + "}": self.positive_peaks,
            "Negative_peaks {potential [V]: dQdV" + f"{self.dQdV_unit}" + "}": self.negative_peaks,
        }

        utils.save_data_as_json(save_dir, added_data, name)

        # save the raw data
        data = utils.assemble_data_frame(**{
            "Time [s]": self.np_time,
            "Voltage [V]": self.np_voltage,
            "Current [A]": self.np_current,
            "Cumulative Charge [C]": self.np_cumulative_charge,
            "dQdV" + f"{self.dQdV_unit}": self.dQdV,
            "dVdt [V/h]": self.dVdt
        })
        data_name = utils.assemble_file_name(optional_name, self.__class__.__name__, "data.csv") if \
                    optional_name else utils.assemble_file_name(self.__class__.__name__, "data.csv")
        utils.save_data_as_csv(save_dir, data, data_name)


    def perform_all_actions(self, save_dir:str, plots:list, optional_name:str = None):
        self.analyze()
        self.plot(save_dir, plots, optional_name=optional_name)
        self.save_data(save_dir=save_dir, optional_name=optional_name)


    def _impute_mean_nearest_neighbors(self, data):
        """Impute NaN values using the mean of nearest neighbors.
        Args:
            data (np.array): data where the NaN values should be imputed
        """
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
        """Calculate the differential of charge with respect to voltage.
        """
        # Convert the cumulative charge from As to mAh
        cumulative_charge_mAh = self.np_cumulative_charge * (1000/3600)

        # Calculate the differential of charge with respect to voltage
        dQdV = np.gradient(cumulative_charge_mAh, self.np_voltage)  # mAh/V
        # Impute NaN values in dQdV using the mean of nearest neighbors
        dQdV_no_nan = self._impute_mean_nearest_neighbors(dQdV)
        # If mass is available, convert it to mAh/gV
        if self.mass_of_active_material is not None:
            dQdV_no_nan /= self.mass_of_active_material  # mAh/gV
            self.dQdV_unit = "mAh/gV"
        elif self.mass_of_active_material is None and self.electrode_area is not None:
            dQdV_no_nan /= self.electrode_area
            self.dQdV_unit = "mAh/cm^2V"
        else:
            self.dQdV_unit = "mAh/V"

        all_peaks, _ = find_peaks(dQdV_no_nan)
        dQdV_no_nan = np.array(dQdV_no_nan)

        # Find all negative peaks if dQdV has negative values
        if np.any(dQdV_no_nan < 0):
            negative_peaks, _ = find_peaks(-dQdV_no_nan)

        # Apply k-means clustering to categorize into two clusters
        n_possible_reactions = self._determine_cluster_number(all_peaks)
        kmeans = KMeans(n_clusters=n_possible_reactions, random_state=42).fit(self.np_voltage[all_peaks].reshape(-1, 1))
        labels = kmeans.labels_
        if np.any(dQdV_no_nan < 0):
            negative_labels = kmeans.predict(self.np_voltage[negative_peaks].reshape(-1, 1))
        # Find the most significant peak in each cluster
        for i in range(n_possible_reactions):
            # Positive Peaks
            cluster_peaks_of_dqdv = dQdV_no_nan[all_peaks][labels == i]
            index_of_max_peak = np.argmax(cluster_peaks_of_dqdv)
            self.positive_peaks[self.np_voltage[all_peaks][labels == i][index_of_max_peak]] =\
                                                dQdV_no_nan[all_peaks][labels == i][index_of_max_peak]

            if np.any(dQdV_no_nan < 0):
                # Negative Peaks
                cluster_neg_peaks = dQdV_no_nan[negative_peaks][negative_labels == i]
                min_peak = np.argmin(cluster_neg_peaks)
                self.negative_peaks[self.np_voltage[negative_peaks][negative_labels == i][min_peak]] =\
                                                dQdV_no_nan[negative_peaks][negative_labels == i][min_peak]

        self.dQdV = dQdV_no_nan


    def _calculate_dVdt(self):
        """Calculate the differential of voltage with respect to time.
        """
        self.dVdt = np.gradient(self.np_voltage, self.np_time) * 3600  # V/h


    def _determine_cluster_number(self, data):
        """Determine the optimal number of clusters using the silhouette score.

        Args:
            data (np.array): data where the cluster number should be determined

        Returns:
            int: optimal number of clusters
        """
        max_silhouette_score = -1
        optimal_n_clusters = 1
        # check if data is 1D
        if len(data.shape) == 1:
            data = data.reshape(-1, 1)
        for n_clusters in range(2, min(len(data), 10)):
            kmeans = KMeans(n_clusters=n_clusters, random_state=0).fit(data)
            silhouette_avg = silhouette_score(data, kmeans.labels_)
            if silhouette_avg > max_silhouette_score:
                max_silhouette_score = silhouette_avg
                optimal_n_clusters = n_clusters

        return optimal_n_clusters


    def _calculate_initial_stabilization_time(self):
        """Calculate the initial stabilization time using the Pelt algorithm.
        """
        model = "l1"  # L1 norm minimization
        algo = rpt.Pelt(model=model).fit(self.np_voltage)
        result = algo.predict(pen=self.penalty_value)

        # The first change point is the end of the initial stabilization phase
        self.tao_initial = self.np_time[result[0]] if result else None
        self.stabilization_values[self.tao_initial] = self.np_voltage[result[0]] if result else None


    def _find_potential_transition_times(self, window_length=73, polyorder=3):
        """Find potential transition times and their corresponding transition voltages.
        This functions excludes the initial stabilization time.

        Args:
            window_length (int): length of the filter window
            polyorder (int): order of the polynomial to fit
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
        #transition_indices = transition_indices[self.np_time[transition_indices] > self.tao_initial]
        if transition_indices.size > 0:
            if len(self.np_time[transition_indices].shape) == 1:
                data = self.np_time[transition_indices].reshape(-1, 1)
            else:
                data = self.np_time[transition_indices]
            n_possible_reactions = self._determine_cluster_number(data)
            if n_possible_reactions != 1:
                kmeans = KMeans(n_clusters=n_possible_reactions, random_state=0).fit(data)
                labels = kmeans.labels_

                for i in range(n_possible_reactions):
                    # check if the self.tao_initial is in the transition_indices then remove the cluster that contains the self.tao_initial
                    if self.tao_initial is not None and self.tao_initial in self.np_time[transition_indices][labels == i]:
                        continue
                    # cluster the peaks
                    cluster_peaks = self.dVdt_smoothed[transition_indices][labels == i]
                    # find the max peak in the cluster
                    max_peak = cluster_peaks[np.argmax(cluster_peaks)]
                    # get the index of the max peak
                    max_peak_index = np.where(self.dVdt_smoothed == max_peak)[0][0]
                    self.transition_values = {self.np_time[max_peak_index]: self.np_voltage[max_peak_index]}
            else:
                # if all the times at the transition_indices are smaller than the self.tao_initial then we do not have a transition
                if np.all(self.np_time[transition_indices] < self.tao_initial):
                    self.transition_values = {}
                else:
                    if self.tao_initial is not None:
                        transition_indices = transition_indices[self.np_time[transition_indices] > self.tao_initial]
                    # max_peak_index = np.argmax(self.dVdt_smoothed[transition_indices])
                    if transition_indices.size > 0:
                        self.transition_values = {self.np_time[i]: self.np_voltage[i] for i in transition_indices}
                #self.transition_value = {self.np_time[i]: self.np_voltage[i] for i in transition_indices}


    def _calculate_diffusion_coefficient(self):
        """Calculate the diffusion coefficient value using Sand's formula without tau.
        """
        # Calculate the coefficient part of the diffusion coefficient using Sand's formula without tau
        # Coefficient = (4 * I^2) / ((n * F * A * c)^2 * pi)
        if self.applied_current is not None:
            current = np.abs(self.applied_current)
        else:
            current = np.abs(np.mean(self.np_current))
        self.d_coefficient = (4 * current**2) / ((self.number_of_electrons * \
                                                self.faraday_constant * \
                                                self.electrode_area * \
                                                self.concentration_of_active_material)**2 * np.pi)


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
