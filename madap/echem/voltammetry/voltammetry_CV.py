""" Voltammetry class for cyclic voltammetry data."""
import os
import time

import numpy as np
import pandas as pd

from scipy.stats import linregress
from scipy.signal import find_peaks

from sklearn.metrics import r2_score
from sklearn.linear_model import LinearRegression

from madap.utils import utils
from madap.echem.voltammetry.voltammetry import Voltammetry
from madap.echem.procedure import EChemProcedure
from madap.logger import logger

from madap.echem.voltammetry.voltammetry_plotting import VoltammetryPlotting as voltPlot

log = logger.get_logger("cyclic_voltammetry")

class Voltammetry_CV(Voltammetry, EChemProcedure):
    """ Class for cyclic voltammetry data."""
    def __init__(self, current, voltage, time_params, cycle_list, args, scan_rate=None) -> None:
        super().__init__(voltage, current, time_params, args=args)
        self.scan_rate = np.array(scan_rate) if scan_rate is not None else None
        self.cycle_indexes = []
        self.cycle_data = {}
        self.forward_scan = {}
        self.backward_scan = {}
        self.direction_index = {}
        self.anodic_peak_params = {}
        self.cathodic_peak_params = {}
        self.E_half_params = {}
        self.smoothing_window_size = 1
        self.fitting_window_size = int(args.fitting_window_size) if args.fitting_window_size is not None else 30
        self.data = None
        self.temperature = float(args.temperature) if args.temperature is not None else 298.15 # Unit: K
        self.cycle_list = cycle_list
        self.tafel_data = {}
        self.regression = False


    def analyze(self):
        """ Analyze the cyclic voltammetry data.
        """
        # create a dataframe from self.scan_rate and self.np_time, self.np_current, self.np_voltage
        self.data = pd.DataFrame({'scan_rate': self.scan_rate, 'time': self.np_time,
                           'current': self.np_current, 'voltage': self.np_voltage})
        # Identify forward and backward scans
        self._find_fwd_bwd_scans()
        # Identify cycles
        self._identify_cycles()
        # Find peak cathodic and anodic currents and their corresponding values
        self._find_peak_currents()
        # calculate the E half
        self._calculate_E_half()
        # calculate the diffusion coefficient from Randles-Sevcik equation
        self._calculate_diffusion_coefficient_anodic_cathodic()
        # calculate the overpotential from the E half for both anodic and cathodic peaks, and height of the peaks
        if self.regression:
            self._find_peak_and_tafel_params()


    def _find_fwd_bwd_scans(self):
        """ Find the forward and backward scans in the data.
        """
        # Determine the initial direction of the scan
        initial_direction = 'F' if self.np_voltage[0] < self.np_voltage[2] else 'B'

        # Initialize variables
        direction = initial_direction
        scan_directions = []

        for i, voltage in enumerate(self.np_voltage):
            # Check if the voltage has reached its extremum and switch direction
            if ((direction=='F') and (voltage < self.np_voltage[i-1]) and (voltage > self.np_voltage[i+1])) or \
                    ((direction=='B') and (voltage > self.np_voltage[i-1]) and (voltage < self.np_voltage[i+1])):
                direction = 'B' if direction == 'F' else 'F'

            scan_directions.append(direction)

        # Add the scan direction data to the dataframe
        self.data['scan_direction'] = scan_directions


    def _identify_cycles(self):
        """ Identify the cycles in the data.
        """
        # Initialize the cycle number and previous direction
        cycle_number = 1
        previous_direction = None
        cycle_numbers = []

        for direction in self.data['scan_direction']:
            if previous_direction and direction != previous_direction:
                # Increment the cycle number if the direction changes
                cycle_number += 1

            cycle_numbers.append((cycle_number + 1) // 2)  # Integer division to pair F and B in the same cycle

            previous_direction = direction

        # add the cycle number to the dataframe
        self.data['cycle_number'] = cycle_numbers


    def _find_peak_currents(self):
        """ Find the peak currents in the data and store them in the appropriate dictionary.
        """
        # Iterate through each cycle and direction
        for cycle in self.data['cycle_number'].unique():
            for direction in ['F', 'B']:
                # Filter the data for the current cycle and direction
                cycle_data = self.data[(self.data['cycle_number'] == cycle) & (self.data['scan_direction'] == direction)].copy()
                # smoothen current
                smoothen_current = cycle_data['current'].rolling(window=1).mean()
                # Identify peaks
                if direction == 'F':  # Forward scan - looking for anodic peaks
                    peaks, _ = find_peaks(smoothen_current, width=5, prominence=smoothen_current.mean()/25)
                    self._store_peak_data(peaks=peaks, data=cycle_data, cycle_num=cycle, peak_type='anodic', scan_direction=direction)
                else:  # Backward scan - looking for cathodic peaks
                    peaks, _ = find_peaks(-smoothen_current, width=5, prominence=smoothen_current.mean()/25)
                    self._store_peak_data(peaks=peaks, data=cycle_data, cycle_num=cycle, peak_type='cathodic', scan_direction=direction)


    def _store_peak_data(self, peaks, data, cycle_num, peak_type, scan_direction):
        """ Store the peak data in the appropriate dictionary.

        Args:
            peaks (list): List of peak indexes
            data (pd.DataFrame): Dataframe containing the data
            cycle_num (int): Cycle number
            peak_type (str): Type of peak (anodic or cathodic)
            scan_direction (str): Scan direction (forward or backward)
        """
        # Store peak data in the appropriate dictionary
        peak_dict = self.cathodic_peak_params if peak_type == 'cathodic' else self.anodic_peak_params
        peak_dict[f'cycle_{cycle_num}'] = {}
        for peak in peaks:
            peak_data = {
                'current': data.iloc[peak]['current'],
                'voltage': data.iloc[peak]['voltage'],
                #'index': data.index[peak],
                'cycle_num': cycle_num,
                'direction': scan_direction,
                'peak_type': 'cathodic' if scan_direction == 'B' else 'anodic',
                'scan_rate': data.iloc[peak]['scan_rate']}
            peak_dict[f'cycle_{cycle_num}'][f'peak_{len(peak_dict[f"cycle_{cycle_num}"]) + 1}'] = peak_data


    def _calculate_E_half(self):
        """ Calculate the half-wave potential for each anodic peak."""
        for cycle, _ in self.anodic_peak_params.items():
            self.E_half_params[cycle] = {}
            min_current_difference = float('inf')
            for anodic_key, anodic_peak in self.anodic_peak_params[cycle].items():
                for cathodic_key , cathodic_peak in self.cathodic_peak_params[cycle].items():
                    current_difference = abs(anodic_peak['current'] + cathodic_peak['current'])

                    if current_difference < min_current_difference:
                        min_current_difference = current_difference

                        average_voltage = (anodic_peak['voltage'] + cathodic_peak['voltage']) / 2
                        peak_to_peak_seperation = abs(anodic_peak['voltage'] - cathodic_peak['voltage'])

                        # find a line between the two peaks and find the intersection with the baseline average voltage
                        line = np.polyfit([anodic_peak['voltage'], cathodic_peak['voltage']], [anodic_peak['current'], cathodic_peak['current']], 1)
                        # find the intersection between the line and x = average_voltage in order to find y = I_half
                        I_half = line[0] * average_voltage + line[1]

                        self.E_half_params[cycle][f"pair_{anodic_key}"] = \
                                {'anodic_peak': anodic_key,
                                'cathodic_peak': cathodic_key,
                                'peak_to_peak_seperation': peak_to_peak_seperation,
                                'E_half': average_voltage,
                                'I_half': I_half} #TODO height of the peaks to the linearly fitted baseline


        # Check if there are any unmatched peaks
        if not self.E_half_params:
            log.info("No matching current pairs found for E_half calculation.")


    def _calculate_diffusion_coefficient_anodic_cathodic(self):
        """ Calculate the diffusion coefficient for each anodic and cathodic peak.
        """
        # Find the highest peak in anodic and cathodic direction
        for cycle, anodic_cycle in self.anodic_peak_params.items():
            if anodic_cycle:
                highest_anodic_peak_key = max(anodic_cycle, key=lambda k, anodic_cycle=anodic_cycle: anodic_cycle[k]['current'])
                D_anodic = self._calculate_diffusion_coefficient(i_peak=anodic_cycle[highest_anodic_peak_key]['current'],
                                                                scan_rate=anodic_cycle[highest_anodic_peak_key]['scan_rate'])
                anodic_cycle[highest_anodic_peak_key]['D'] = D_anodic
                log.info(f"Diffusion coefficient for cycle {cycle} and {highest_anodic_peak_key} is {D_anodic}")
            else:
                log.info(f"No anodic peak found for cycle {cycle}")

            if self.cathodic_peak_params[cycle]:
                highest_cathodic_peak_key = max(self.cathodic_peak_params[cycle], \
                    key=lambda k, cycle=cycle: self.cathodic_peak_params[cycle][k]['current'])
                # Calculate D for cathodic peaks
                D_cathodic = self._calculate_diffusion_coefficient(i_peak=self.cathodic_peak_params[cycle][highest_cathodic_peak_key]['current'],
                                                                   scan_rate=self.cathodic_peak_params[cycle][highest_cathodic_peak_key]['scan_rate'])
                # Add D to the peak dictionaries
                self.cathodic_peak_params[cycle][highest_cathodic_peak_key]['D'] = D_cathodic
                log.info(f"Diffusion coefficient for cycle {cycle} and {highest_cathodic_peak_key} is {D_cathodic}")
            else:
                log.info(f"No cathodic peak found for cycle {cycle}")


    def _calculate_diffusion_coefficient(self, i_peak, scan_rate):
        """ Calculate the diffusion coefficient from the Randles-Sevcik equation.

        Args:
            i_peak (float): Peak current
            scan_rate (float): Scan rate

        Returns:
            float: Diffusion coefficient
        """
        # Constants
        const_298K = 2.69 * 10**5
        const_other_temp = 0.4463
        if scan_rate is None:
            log.warning("No scan rate found in the data. Using 1 V/s as default.")
            scan_rate = 1

        if int(self.temperature) == 298:
            # Randles-Sevcik equation
            #i_peak [A] = 2.69 * 10**5 * n**(3/2) * A * C * v**(1/2) * D**(1/2) with A [cm^2], C [mol/cm^3], v [V/s], D [cm^2/s]
            denominator = (const_298K * self.number_of_electrons**(3/2) * self.electrode_area * \
                self.concentration_of_active_material * (scan_rate**0.5))
            return (i_peak / denominator)**2
        # Randles-Sevcik equation
        #i_peak [A] = 0.4463 * n * F * A * C * (n**(1/2) * v**(1/2) * D**(1/2)/R*T)**(1/2) with A [cm^2], C [mol/cm^3], v [V/s], D [cm^2/s]
        coefficient = ((self.number_of_electrons * self.faraday_constant * scan_rate)/\
                        (self.gas_constant * self.temperature))**0.5
        denominator = const_other_temp * self.number_of_electrons * self.faraday_constant * \
            self.electrode_area * self.concentration_of_active_material * coefficient
        return (i_peak / denominator)**2


    def _find_peak_and_tafel_params(self):
        """ Find the peak parameters for each anodic and cathodic peak.
        """
        for cycle, tafel_data in self.E_half_params.items():
            tafel_data = {}
            for pair in self.E_half_params[cycle].keys():
                tafel_data[pair] = {}
                peak_anodic_number = self.E_half_params[cycle][pair]['anodic_peak']
                peak_cathodic_number = self.E_half_params[cycle][pair]['cathodic_peak']

                # calculate the overpotential
                self._find_overpotential(cycle, pair, peak_anodic_number, peak_cathodic_number)
                cycle_number = int(cycle.split("_")[1])
                # check if the cathodic peak  can be calculated
                if self.data.loc[(self.data['voltage'] > self.anodic_peak_params[cycle][peak_anodic_number]['voltage']) & \
                                 (self.data['cycle_number'] == cycle_number) & \
                                 (self.data['scan_direction'] == "B")].empty:
                    log.warning("No voltage values higher than the half voltage and in the same cycle and \
                                backward scan and the height of the cathodic peak current cannot be calculated")
                else:
                    # filtered cathodic data
                    filter_cathodic_data = self.data[(self.data['cycle_number'] == cycle_number) & (self.data['scan_direction'] == "B")].copy()
                    self._find_height_of_cathodic_peak_current(cycle, pair, peak_cathodic_number, filter_cathodic_data )

                # check if the anodic peak  can be calculated
                if self.data.loc[(self.data['voltage'] < self.cathodic_peak_params[cycle][peak_cathodic_number]['voltage']) & \
                                 (self.data['cycle_number'] == cycle_number) & \
                                 (self.data['scan_direction'] == "F")].empty:
                    log.warning("No voltage values lower than the half voltage and in the same cycle and \
                        forward scan and the height of the anodic peak current cannot be calculated")
                else:
                    # filtered anodic data
                    filter_anodic_data = self.data[(self.data['cycle_number'] == cycle_number) & (self.data['scan_direction'] == "F")].copy()
                    self._find_height_of_anodic_peak_current(cycle, pair, peak_anodic_number, filter_anodic_data )

                log.info(f"Finished calculating the height of the peaks for cycle {cycle} and pair {pair}")
                self._find_tafel_region(cycle, peak_number=peak_cathodic_number, reaction_type="cathodic")
                self._find_tafel_region(cycle, peak_number=peak_anodic_number, reaction_type="anodic")
                log.info(f"Finished calculating the peak parameters for cycle {cycle} and pair {pair}")
                self._calculate_corrosion_point(cycle, peak_anodic_number, peak_cathodic_number)
                log.info(f"Finished calculating the corrosion point for cycle {cycle} and pair {pair}")


    def _find_overpotential(self, cycle, pair, peak_anodic_number, peak_cathodic_number):
        """ Find the overpotential for the anodic and cathodic peaks.

        Args:
            cycle (str): Cycle number
            pair (str): Pair number of the anodic and cathodic peak
            peak_anodic_number (str): Peak number of the anodic peak
            peak_cathodic_number (str): Peak number of the cathodic peak
        """
        # Calculate the overpotential for the anodic peak
        self.E_half_params[cycle][pair]['anodic_overpotential'] =\
            self.anodic_peak_params[cycle][peak_anodic_number]['voltage'] - self.E_half_params[cycle][pair]['E_half']
        # Calculate the overpotential for the cathodic peak
        self.E_half_params[cycle][pair]['cathodic_overpotential'] =\
            self.cathodic_peak_params[cycle][peak_cathodic_number]['voltage']  - self.E_half_params[cycle][pair]['E_half']


    def _find_height_of_cathodic_peak_current(self, cycle, pair, peak_cathodic_number, filter_cathodic_data):
        """ Find the height of the cathodic peak current. The height is the distance between the peak current
            and the intersection of the linearly fitted line with the peak.

        Args:
            cycle (str): Cycle number
            pair (str): Pair number of the anodic and cathodic peak
            peak_cathodic_number (str): Peak number of the cathodic peak
            filter_cathodic_data (pd.DataFrame): Filtered cathodic data
        """
        max_distance = 0
        best_line = None
        # find the cathodic peak current
        cathodic_peak_current = self.cathodic_peak_params[cycle][peak_cathodic_number]["current"]
        cathodic_peak_voltage = self.cathodic_peak_params[cycle][peak_cathodic_number]["voltage"]
        # Smoothen the filtered data
        smoothened_data = filter_cathodic_data.copy()
        smoothened_data["current"] = smoothened_data['current'].rolling(window=self.smoothing_window_size).mean()
        # find the index of the voltage where the current is half of the peak current
        index_of_I_half_voltage = max(filter_cathodic_data.index[filter_cathodic_data['voltage'] >= self.E_half_params[cycle][pair]['E_half']])
        # find the fitting window size
        fitting_window = int(len(filter_cathodic_data[:index_of_I_half_voltage]) / 6) #self.fitting_window_size)

        for i in range(len(smoothened_data.loc[:index_of_I_half_voltage])):
            # select two points and fit a line

            point1, point2 = smoothened_data.iloc[i], smoothened_data.iloc[i+fitting_window]
            # check if the points are not nan
            if (abs(point1["current"]) < abs(point2["current"])) and (point1["voltage"] != point2["voltage"]):
                slope, intercept, r_value, _, _ = linregress([point1['voltage'], point2['voltage']],
                                                [point1['current'], point2['current']])
                r2 = r_value**2
                # find the intersection between the line and x = cathodic_peak_voltage in order to find y = I_height
                intersect_y = self._calculate_intersection(slope, intercept, cathodic_peak_voltage)
                if intersect_y > cathodic_peak_current:
                    # calculate the distance between the peak current and the intersection
                    distance_to_peak = abs(cathodic_peak_current) - abs(intersect_y)
                    if (distance_to_peak > max_distance) and (r2 > 0.99):
                        best_point1, best_point2 = point1, point2
                        max_distance = distance_to_peak
                        best_line = (slope, intercept)

        # check if the distance is zero
        if max_distance == 0:
            log.warning(f"No line found for cycle {cycle} and pair {pair} and cathodic peak {peak_cathodic_number}. \
                Increase the smoothing window size or the fitting window size.")
        else:
            # store the height of the peak current
            self.cathodic_peak_params[cycle][peak_cathodic_number]["height"] = max_distance
            self.cathodic_peak_params[cycle][peak_cathodic_number]["capacitative_line"] = best_line
            self.cathodic_peak_params[cycle][peak_cathodic_number]["capacitative_start_point"] = best_point1
            self.cathodic_peak_params[cycle][peak_cathodic_number]["capacitative_end_point"] = best_point2
            self.E_half_params[cycle][pair]['cathodic_peak_height'] = max_distance


    def _find_height_of_anodic_peak_current(self, cycle, pair, peak_anodic_number, filter_anodic_data):
        """ Find the height of the anodic peak current. The height is the distance between the peak current

        Args:
            cycle (str): Cycle number
            pair (str): Pair number of the anodic and cathodic peak
            peak_anodic_number (str): Peak number of the anodic peak
            filter_anodic_data (pd.DataFrame): Filtered anodic data
        """
        max_distance = 0
        best_line = None
        # find the anodic peak current
        anodic_peak_current = self.anodic_peak_params[cycle][peak_anodic_number]["current"]
        anodic_peak_voltage = self.anodic_peak_params[cycle][peak_anodic_number]["voltage"]
        # Smoothen the filtered data
        filter_anodic_data['current'] = filter_anodic_data['current'].rolling(window=self.smoothing_window_size).mean()
        index_of_I_half_voltage = max(filter_anodic_data.index[filter_anodic_data['voltage'] <= self.E_half_params[cycle][pair]['E_half']])
        fitting_window = int(len(filter_anodic_data[:index_of_I_half_voltage]) / 6) #self.fitting_window_size)

        for i in range(len(filter_anodic_data.loc[:index_of_I_half_voltage-fitting_window])):
            # select two points and fit a line
            point1, point2 = filter_anodic_data.iloc[i], filter_anodic_data.iloc[i+fitting_window]
            if (abs(point1["current"]) > abs(point2["current"])) and (point1["voltage"] != point2["voltage"]):
                slope, intercept, r_value, _, _ = linregress([point1['voltage'], point2['voltage']],
                                                [point1['current'], point2['current']])
                r2 = r_value**2
                intersect_y = self._calculate_intersection(slope, intercept, anodic_peak_voltage)
                if intersect_y < anodic_peak_current:
                    distance_to_peak = anodic_peak_current - intersect_y
                    if (distance_to_peak > max_distance) and (r2 > 0.99):
                        best_point1, best_point2 = point1, point2
                        max_distance = distance_to_peak
                        best_line = (slope, intercept)
        if max_distance == 0:
            log.warning(f"No line found for cycle {cycle} and pair {pair} and anodic peak {peak_anodic_number}. \
                Increase the smoothing window size or the fitting window size.")
        else:
            self.anodic_peak_params[cycle][peak_anodic_number]["height"] = max_distance
            self.anodic_peak_params[cycle][peak_anodic_number]["capacitative_line"] = best_line
            self.anodic_peak_params[cycle][peak_anodic_number]["capacitative_start_point"] = best_point1
            self.anodic_peak_params[cycle][peak_anodic_number]["capacitative_end_point"] = best_point2
            self.E_half_params[cycle][pair]['anodic_peak_height'] = max_distance


    def _calculate_intersection(self, line_slope, line_intercept, peak_v):
        """
        Calculate the intersection of the fitted line with the vertical line through the peak.
        The equation of the vertical line is x = peak_i (voltage).
        The equation of the fitted line is y = line_slope * x + line_intercept.

        Args:
            line_slope (float): Slope of the fitted line
            line_intercept (float): Intercept of the fitted line
            peak_v (float): Voltage of the peak

        Returns:
            float: Intersection of the fitted line with the vertical line through the peak
        """
        intersect_i = line_slope * peak_v + line_intercept
        return intersect_i


    def _sort_and_transform_data(self, data_for_fitting, reaction_type):
        """ Sort the data and transform the current to log(current).

        Args:
            data_for_fitting (pd.DataFrame): Dataframe containing the data
            reaction_type (str): Type of reaction (anodic or cathodic)
        Returns:
            pd.DataFrame: Sorted dataframe
        """
        if reaction_type == "anodic":
            sorted_data = data_for_fitting.sort_values(by="voltage", ascending=False)
        elif reaction_type == "cathodic":
            sorted_data = data_for_fitting.sort_values(by="voltage", ascending=True)

        sorted_data["log_current"] = np.log10(abs(sorted_data["current"]))
        return sorted_data


    def _find_tafel_region(self, cycle, peak_number, reaction_type, max_points=None):
        """ Find the Tafel region for the anodic and cathodic peaks.

        Args:
            cycle (str): Cycle number
            peak_number (str): Peak number of the anodic or cathodic peak
            reaction_type (str): Type of reaction (anodic or cathodic)
            max_points (int, optional): Maximum number of points to consider for the linear regression. Defaults to None.
        """
        self.tafel_data[cycle][f"pair_{peak_number}"][reaction_type] = {}
        # fit the best line on the log-transformed current (y) and voltage (x)
        scan_direction = "B" if reaction_type == "cathodic" else "F"
        cycle_number = int(cycle.split("_")[1])
        e_half = self.E_half_params[cycle][f"pair_{peak_number}"]["E_half"]
        # filter the data
        data = self.data[(self.data['cycle_number'] == cycle_number) & (self.data['scan_direction'] == scan_direction)].copy()
        # filter the data between the peak voltage and the half voltage or between the peak voltage and the next peak voltage
        data_for_fitting = self._check_multiple_peaks(data=data, cycle=cycle, peak_number=peak_number,
                                                      reaction_type=reaction_type, e_half=e_half)
        # add the self.tafel_data to the dictionary
        if reaction_type == "anodic":
            data_for_peak_one = data[data["voltage"] < self.anodic_peak_params[cycle][f"{peak_number}"]["voltage"]]
        else:
            data_for_peak_one = data[data["voltage"] > self.cathodic_peak_params[cycle][f"{peak_number}"]["voltage"]]
        self.tafel_data[cycle][f"pair_{peak_number}"][reaction_type] = data_for_peak_one if peak_number == "peak_1" else data_for_fitting

        # remove the data points where the current is zero because it will cause an error in the log transformation
        data_for_fitting = data_for_fitting[data_for_fitting["current"] != 0]

        sorted_data = self._sort_and_transform_data(data_for_fitting, reaction_type)
        self._linear_regression_fit(sorted_data, cycle, peak_number, reaction_type, max_points)
        # sorted_data["log_current"] = np.log10(abs(sorted_data["current"]))


    def _linear_regression_fit(self, sorted_data, cycle, peak_number, reaction_type, max_points=None):
        """ Fit the linear regression model to the data and store the best fit parameters.

        Args:
            sorted_data (pd.DataFrame): Sorted dataframe
            cycle (str): Cycle number
            peak_number (str): Peak number of the anodic or cathodic peak
            reaction_type (str): Type of reaction (anodic or cathodic)
            max_points (int, optional): Maximum number of points to consider for the linear regression. Defaults to None.
        """
        # initialize the best fit parameters
        best_fit_slope = 0
        best_fit_r2 = float("-inf")
        best_fit_size = None

        # Determine the maximum number of points to consider if not specified
        if max_points is None:
            max_points = len(sorted_data)

        # specify the minimum number of points to consider
        min_points = int(len(sorted_data)/4) if int(len(sorted_data)/4) > 6 else 6

        # iterate through the data
        log.info(f"Start fitting the linear regression model for cycle {cycle} and {reaction_type} peak {peak_number}")
        log.info("This can take a while. Please be patient.")
        # Take the starting point in time before the loop
        start_time = time.time()
        # start the sorted data from the first point and iterate through the data
        for start_ind in range(0, len(sorted_data), 1):
            subset_of_sorted_data = sorted_data.iloc[start_ind:]
            if best_fit_r2 > 0.98:
                break
            for size in range(min_points, max_points + 1, 2):
                subset = subset_of_sorted_data.head(size)
                X_data = subset[['voltage']]
                y_data = subset['log_current']

                # Fit the linear regression model
                model = LinearRegression(n_jobs=4).fit(X_data, y_data)
                y_pred = model.predict(X_data)

                # Calculate R^2 value
                r2 = r2_score(y_data, y_pred)
                # Update the best fit parameters if the R^2 value is higher
                if r2 > best_fit_r2:
                    # Write the start and end points of the best fit line
                    start_point = {"voltage": X_data['voltage'].iloc[0],
                                "current": subset['current'].iloc[0],
                                "log_current": subset['log_current'].iloc[0]}
                    end_point = {"voltage": X_data['voltage'].iloc[-1],
                                "current": subset['current'].iloc[-1],
                                "log_current": subset['log_current'].iloc[-1]}
                    best_fit_slope = model.coef_[0]
                    best_fit_intercept = model.intercept_
                    best_fit_r2 = r2
                    best_fit_size = size

        if best_fit_r2 < 0.98:
            log.warning(f"R^2 value is {best_fit_r2:.2f}. The slope and intercept of the Tafel region might not be accurate.")
        # Slope = (alpha*F*n)/(2.3*R*T). Find alpha
        alpha = (best_fit_slope * 2.3 * self.gas_constant * self.temperature) /(self.faraday_constant * self.number_of_electrons)
        end_time = time.time()
        log.info(f"Finished fitting the linear regression model for cycle {cycle} and {reaction_type} \
            peak {peak_number} in {(end_time - start_time):.2f} seconds.")
        log.info(f"Best R^2 value is {best_fit_r2:.2f}.")

        if reaction_type == "anodic":
            self.anodic_peak_params[cycle][peak_number]["faradaic_slope"] = best_fit_slope
            self.anodic_peak_params[cycle][peak_number]["faradaic_intercept"] = best_fit_intercept
            self.anodic_peak_params[cycle][peak_number]["faradaic_r2"] = best_fit_r2
            self.anodic_peak_params[cycle][peak_number]["faradaic_size"] = best_fit_size
            self.anodic_peak_params[cycle][peak_number]["faradaic_start_point"] = start_point
            self.anodic_peak_params[cycle][peak_number]["faradaic_end_point"] = end_point
            self.anodic_peak_params[cycle][peak_number]["alpha"] = alpha

        elif reaction_type == "cathodic":
            self.cathodic_peak_params[cycle][peak_number]["faradaic_slope"] = best_fit_slope
            self.cathodic_peak_params[cycle][peak_number]["faradaic_intercept"] = best_fit_intercept
            self.cathodic_peak_params[cycle][peak_number]["faradaic_r2"] = best_fit_r2
            self.cathodic_peak_params[cycle][peak_number]["faradaic_size"] = best_fit_size
            self.cathodic_peak_params[cycle][peak_number]["faradaic_start_point"] = start_point
            self.cathodic_peak_params[cycle][peak_number]["faradaic_end_point"] = end_point
            self.cathodic_peak_params[cycle][peak_number]["alpha"] = alpha


    def _check_multiple_peaks(self, data, cycle, peak_number, reaction_type, e_half):
        """ Check if there are multiple peaks in the same cycle and filter the data accordingly.

        Args:
            data (pd.DataFrame): Dataframe containing the data
            cycle (str): Cycle number
            peak_number (str): Peak number of the anodic or cathodic peak
            reaction_type (str): Type of reaction (anodic or cathodic)
            e_half (float): Half-wave potential

        Returns:
            pd.DataFrame: Filtered dataframe
        """
        peaks = self.anodic_peak_params if reaction_type == "anodic" else self.cathodic_peak_params
        cycle_peaks = peaks[cycle]
        # total number of peaks
        number_of_peaks = len(cycle_peaks)
        current_peak_index = int(peak_number.split('_')[1])

        def get_filtered_voltage(index):
            """ Get the filtered voltage.

            Args:
                index (int): Index of the peak

            Returns:
                float: Filtered voltage
            """
            return (cycle_peaks[f"peak_{index}"]["voltage"]) + (cycle_peaks[f"peak_{index + 1}"]["voltage"]) / 2

        # check if there is only one peak or the current peak is the first peak
        if number_of_peaks == 1 or current_peak_index == 1:
            # offset = 1.05 if cycle_peaks[peak_number]["voltage"] > e_half else 0.95
            # define the condition to filter the data between the peak voltage and the half voltage
            if reaction_type == "anodic": # get the voltage above the E_half and below the anodic peak voltage
                condition = (data["voltage"] > e_half) & (data["voltage"] < (cycle_peaks[peak_number]["voltage"]))
            else: # get the voltage below the E_half and above the cathodic peak voltage
                condition = (data["voltage"] < e_half) & (data["voltage"] > (cycle_peaks[peak_number]["voltage"]))

        # check if the current peak is less than the total number of peaks and the current peak is not the first peak
        elif current_peak_index > 1 and current_peak_index < number_of_peaks:
            # get the voltage between the current peak and the previous peak
            lower_voltage = get_filtered_voltage(current_peak_index - 1)
            # get the voltage between the current peak and the next peak
            upper_voltage = cycle_peaks[f"peak_{current_peak_index}"]["voltage"]
            # define the condition to filter the data between the two voltages
            if reaction_type == "anodic":
                condition = (data["voltage"] > lower_voltage) & (data["voltage"] < upper_voltage)
            else:
                condition = (data["voltage"] < lower_voltage) & (data["voltage"] > upper_voltage)

        # check if the current peak is the last peak
        elif current_peak_index == number_of_peaks:
            filtered_voltage = get_filtered_voltage(current_peak_index - 1)
            condition = data["voltage"] > filtered_voltage if reaction_type == "anodic" else data["voltage"] < filtered_voltage

        else:
            log.error(f"Peak number {current_peak_index} is not valid.")

        return data[condition].copy()


    def _calculate_corrosion_point(self, cycle, peak_anodic_number, peak_cathodic_number):
                                   #slope1, intercept1, slope2, intercept2):
        """ Calculate the intersection of two lines.

        Args:
            slope1 (float): Slope of the first line
            intercept1 (float): Intercept of the first line
            slope2 (float): Slope of the second line
            intercept2 (float): Intercept of the second line

        Returns:
            float: Intersection of the two lines
        """
        # check if the lines are parallel
        slope2 = self.anodic_peak_params[cycle][peak_anodic_number]["faradaic_slope"]
        slope1 = self.cathodic_peak_params[cycle][peak_cathodic_number]["faradaic_slope"]
        intercept2 = self.anodic_peak_params[cycle][peak_anodic_number]["faradaic_intercept"]
        intercept1 = self.cathodic_peak_params[cycle][peak_cathodic_number]["faradaic_intercept"]

        if slope1 == slope2:
            log.error("The two lines are parallel and do not intersect.")
        # find the x coordinate of the intersection
        x_point = (intercept2 - intercept1) / (slope1 - slope2)
        # find the y coordinate of the intersection
        y_point = slope1 * x_point + intercept1 # current is in log scale
        y_point_linear = np.exp(y_point) # convert the current back to linear scale
        self.E_half_params[cycle][f"pair_{peak_anodic_number}"]["corrosion_point"] = {}
        self.E_half_params[cycle][f"pair_{peak_anodic_number}"]["corrosion_point"]["voltage"] = x_point
        self.E_half_params[cycle][f"pair_{peak_anodic_number}"]["corrosion_point"]["log_current"] = y_point
        self.E_half_params[cycle][f"pair_{peak_anodic_number}"]["corrosion_point"]["current"] = y_point_linear


    def plot(self, save_dir, plots, optional_name: str = None):
        """Plot the data

        Args:
            save_dir (str): The directory where the plot should be saved
            plots (list): List of plots to plot
            optional_name (str, optional): Optional name of the plot. Defaults to None.
        """

        plot_dir = utils.create_dir(os.path.join(save_dir, "plots"))
        plot = voltPlot(current=self.np_current, voltage=self.np_voltage, time=self.np_time,
                        electrode_area=self.electrode_area,
                        mass_of_active_material=self.mass_of_active_material,
                        cumulative_charge = self.cumulative_charge,
                        procedure_type=self.__class__.__name__)
        if (self.data["scan_rate"].isnull().values.all()) and ("Peak Scan" in plots):
            log.warning("Scan rate is not found in the data so no Plot is possible. Please provide the scan rate.")
            # Drop the Peak scan plot from the list of plots
            plots = [plot for plot in plots if plot != "Peak Scan"]

        tafel_present = "Tafel" in plots
        cv_present = "CV" in plots

        if len(plots) != 0:
            fig, available_axes = plot.compose_volt_subplot(plots=plots)
            for sub_ax, plot_name in zip(available_axes, plots):

                if plot_name == "E-t":
                    sub_ax = available_axes[-1] if (tafel_present and cv_present and (len(plots) == 3)) else \
                            available_axes[0] if (len(plots) == 5) else sub_ax
                    plot.potential_waveform(subplot_ax=sub_ax, data=self.data)
                elif plot_name == "I-t":
                    sub_ax = available_axes[-1] if (tafel_present and cv_present and (len(plots) == 3)) else \
                            available_axes[4] if (len(plots) == 5) else sub_ax

                    plot.CA(subplot_ax=sub_ax, x_lim_min="auto", y_lim_min="auto", legend=False)
                elif plot_name == "Peak Scan":
                    sub_ax = available_axes[-1] if (tafel_present and cv_present and (len(plots) == 3)) else \
                            available_axes[3] if (len(plots) == 5) else sub_ax
                    plot.peak_scan(subplot_ax=sub_ax, anodic_peak_params=self.anodic_peak_params,
                                cathodic_peak_params=self.cathodic_peak_params, E_half_params=self.E_half_params)

                elif plot_name == "CV":
                    sub_ax = available_axes[-1] if ((not tafel_present) and (len(plots) == 3)) else \
                        available_axes[0] if (tafel_present and (len(plots) == 3)) else \
                        available_axes[2] if (tafel_present and (len(plots) == 5)) else sub_ax
                    plot.CV(subplot_ax=sub_ax, data=self.data, anodic_peak_params=self.anodic_peak_params,
                            cathodic_peak_params=self.cathodic_peak_params,
                            cycle_list=self.cycle_list)
                elif plot_name == "Tafel":
                    sub_ax = available_axes[-1] if ((not cv_present) and (len(plots) == 3)) else\
                        available_axes[1] if (cv_present and (len(plots) == 3)) else \
                        available_axes[1] if (cv_present and (len(plots) == 5)) else sub_ax
                    plot.Tafel(subplot_ax=sub_ax, data=self.tafel_data, anodic_peak_params=self.anodic_peak_params,
                               cathodic_peak_params=self.cathodic_peak_params, E_half_params=self.E_half_params,
                               cycle_list=self.cycle_list)

                else:
                    log.error("Voltammetry CP class does not have the selected plot.")
                    continue

            self.save_figure(fig, plot, optional_name=optional_name, plot_dir=plot_dir)

        else:
            raise ValueError("No plot is selected. Please select a plot.")


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

        added_data = {**self.E_half_params, **self.anodic_peak_params, **self.cathodic_peak_params,
                    "Smoothing window size": self.smoothing_window_size,
                    "Fitting window size": self.fitting_window_size,
                    "Temperature [K]": self.temperature}

        processed_data = utils.convert_numpy_to_python(added_data)
        utils.save_data_as_json(save_dir, processed_data, name)

        self._save_data_with_name(optional_name, self.__class__.__name__, save_dir, self.data)


    def perform_all_actions(self, save_dir:str, plots:list, optional_name:str = None):
        """Perform all the actions: analyze, plot and save the data.

        Args:
            save_dir (str): The directory where the data should be saved
            plots (list): List of plots to plot
            optional_name (str): The optional name of the data.
        Raises:
            ValueError: If no plot is selected or in case the plot is not available.
        """
        self.regression = False
        if "Tafel" in plots:
            self.regression = True
        self.analyze()
        try:
            self.plot(save_dir, plots, optional_name=optional_name)
        except ValueError as e:
            raise e
        #self.save_data(save_dir=save_dir, optional_name=optional_name)


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
