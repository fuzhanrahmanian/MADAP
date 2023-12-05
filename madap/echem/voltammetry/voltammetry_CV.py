""" Voltammetry class for cyclic voltammetry data."""
import numpy as np
import pandas as pd
from scipy.stats import linregress
from sklearn.metrics import silhouette_score
from scipy.signal import find_peaks
from madap.echem.voltammetry.voltammetry import Voltammetry
from madap.echem.procedure import EChemProcedure
from madap.logger import logger


log = logger.get_logger("cyclic_voltammetry")


class Voltammetry_CV(Voltammetry, EChemProcedure):
    """ Class for cyclic voltammetry data."""
    def __init__(self, current, voltage, time, args, scan_rate=None) -> None:
        super().__init__(voltage, current, time, args=args)
        self.scan_rate = np.array(scan_rate) if scan_rate is not None else None
        self.applied_scan_rate = float(args.applied_scan_rate) if args.applied_scan_rate is not None else None
        self.cycle_indexes = []
        self.cycle_data = {}
        self.forward_scan = {}
        self.backward_scan = {}
        self.direction_index = {}
        self.anodic_peak_current = {}
        self.cathodic_peak_current = {}
        self.E_half = {}
        #self.window_size = 2 #int(args.window_size) if args.window_size is not None else 10
        self.smoothing_window_size = 5
        self.fitting_window_size = int(args.fitting_window_size) if args.fitting_window_size is not None else 30
        self.data = None
        self.temperature = float(args.temperature) if args.temperature is not None else 298.15 # Unit: K

    def analyze(self):

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
        # calculate the overpotential from the E half for both anodic and cathodic peaks
        self._find_peak_params()
        # calculate the half current
        #self._find_height_of_peak_current()
        # todo: find the height of the peak current to the linearly fitted baseline
        # todo: find the capacitative and faradaic current
        # todo: get the two linear lines from Tafel plot and calculate the E_corr and I_corr



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
        peak_dict = self.cathodic_peak_current if peak_type == 'cathodic' else self.anodic_peak_current
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
        for cycle in self.anodic_peak_current.keys():
            self.E_half[cycle] = {}
            min_current_difference = float('inf')
            for anodic_key, anodic_peak in self.anodic_peak_current[cycle].items():
                for cathodic_key , cathodic_peak in self.cathodic_peak_current[cycle].items():
                    current_difference = abs(anodic_peak['current'] + cathodic_peak['current'])

                    if current_difference < min_current_difference:
                        min_current_difference = current_difference

                        average_voltage = (anodic_peak['voltage'] + cathodic_peak['voltage']) / 2
                        peak_to_peak_seperation = abs(anodic_peak['voltage'] - cathodic_peak['voltage'])

                        # find a line between the two peaks and find the intersection with the baseline average voltage
                        line = np.polyfit([anodic_peak['voltage'], cathodic_peak['voltage']], [anodic_peak['current'], cathodic_peak['current']], 1)
                        # find the intersection between the line and x = average_voltage in order to find y = I_half
                        I_half = line[0] * average_voltage + line[1]

                        self.E_half[cycle][f"pair_{anodic_key}"] = \
                                {'anodic_peak': anodic_key,
                                'cathodic_peak': cathodic_key,
                                'peak_to_peak_seperation': peak_to_peak_seperation,
                                'E_half': average_voltage,
                                'I_half': I_half} #TODO height of the peaks to the linearly fitted baseline

        # Check if there are any unmatched peaks
        if not self.E_half:
            log.info("No matching current pairs found for E_half calculation.")


    def _calculate_diffusion_coefficient_anodic_cathodic(self):
        """ Calculate the diffusion coefficient for each anodic and cathodic peak.
        """
        # Find the highest peak in anodic and cathodic direction
        for cycle in self.anodic_peak_current.keys():
            if self.anodic_peak_current[cycle]:
                highest_anodic_peak_key = max(self.anodic_peak_current[cycle], key=lambda k: self.anodic_peak_current[cycle][k]['current'])
                D_anodic = self._calculate_diffusion_coefficient(self.anodic_peak_current[cycle][highest_anodic_peak_key]['current'], self.anodic_peak_current[cycle][highest_anodic_peak_key]['scan_rate'])
                self.anodic_peak_current[cycle][highest_anodic_peak_key]['D'] = D_anodic
                log.info(f"Diffusion coefficient for cycle {cycle} and {highest_anodic_peak_key} is {D_anodic}")
            else:
                log.info(f"No anodic peak found for cycle {cycle}")

            if self.cathodic_peak_current[cycle]:
                highest_cathodic_peak_key = max(self.cathodic_peak_current[cycle], key=lambda k: self.cathodic_peak_current[cycle][k]['current'])
                # Calculate D for cathodic peaks
                D_cathodic = self._calculate_diffusion_coefficient(self.cathodic_peak_current[cycle][highest_cathodic_peak_key]['current'], self.cathodic_peak_current[cycle][highest_cathodic_peak_key]['scan_rate'])
                # Add D to the peak dictionaries
                self.cathodic_peak_current[cycle][highest_cathodic_peak_key]['D'] = D_cathodic
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
            if self.applied_scan_rate is not None:
                scan_rate = self.applied_scan_rate
            elif not self.data["scan_rate"].isnull().values.all():
                    scan_rate = self.data["scan_rate"].mean()
            else:
                log.warning("No scan rate found in the data. Using 1 V/s as default.")
                scan_rate = 1

        if int(self.temperature) == 298:
            # Randles-Sevcik equation
            #i_peak [A] = 2.69 * 10**5 * n**(3/2) * A * C * v**(1/2) * D**(1/2) with A [cm^2], C [mol/cm^3], v [V/s], D [cm^2/s]
            denominator = (const_298K * self.number_of_electrons**(3/2) * self.electrode_area * self.concentration_of_active_material * (scan_rate**0.5))
            return (i_peak / denominator)**2
        else:
            # Randles-Sevcik equation
            #i_peak [A] = 0.4463 * n * F * A * C * (n**(1/2) * v**(1/2) * D**(1/2)/R*T)**(1/2) with A [cm^2], C [mol/cm^3], v [V/s], D [cm^2/s]
            coefficient = ((self.number_of_electrons * self.faraday_constant * scan_rate)/(self.gas_constant * self.temperature))**0.5
            denominator = (const_other_temp * self.number_of_electrons * self.faraday_constant * self.electrode_area * self.concentration_of_active_material * coefficient)
            return (i_peak / denominator)**2


    def _find_peak_params(self):
        """ Find the peak parameters for each anodic and cathodic peak.
        """
        for cycle in self.E_half:
            for pair in self.E_half[cycle].keys():
                peak_anodic_number = self.E_half[cycle][pair]['anodic_peak']
                peak_cathodic_number = self.E_half[cycle][pair]['cathodic_peak']

                # calculate the overpotential
                self._find_overpotential(cycle, pair, peak_anodic_number, peak_cathodic_number)

                cycle_number = int(cycle.split("_")[1])
                # check if the cathodic peak  can be calculated
                if self.data.loc[(self.data['voltage'] > self.anodic_peak_current[cycle][peak_anodic_number]['voltage']) & \
                                 (self.data['cycle_number'] == cycle_number) & \
                                 (self.data['scan_direction'] == "B")].empty:
                    log.warning("No voltage values higher than the half voltage and in the same cycle and backward scan and the height of the cathodic peak current cannot be calculated")
                else:
                    # filtered cathodic data
                    filter_cathodic_data = self.data[(self.data['cycle_number'] == cycle_number) & (self.data['scan_direction'] == "B")].copy()
                    self._find_height_of_cathodic_peak_current(cycle, pair, peak_cathodic_number, filter_cathodic_data )

                # check if the anodic peak  can be calculated
                if self.data.loc[(self.data['voltage'] < self.cathodic_peak_current[cycle][peak_cathodic_number]['voltage']) & \
                                 (self.data['cycle_number'] == cycle_number) & \
                                 (self.data['scan_direction'] == "F")].empty:
                    log.warning("No voltage values lower than the half voltage and in the same cycle and forward scan and the height of the anodic peak current cannot be calculated")
                else:
                    # filtered anodic data
                    filter_anodic_data = self.data[(self.data['cycle_number'] == cycle_number) & (self.data['scan_direction'] == "F")].copy()
                    self._find_height_of_anodic_peak_current(cycle, pair, peak_anodic_number, filter_anodic_data )


    def _find_overpotential(self, cycle, pair, peak_anodic_number, peak_cathodic_number):
        """ Find the overpotential for the anodic and cathodic peaks.

        Args:
            cycle (str): Cycle number
            pair (str): Pair number of the anodic and cathodic peak
            peak_anodic_number (str): Peak number of the anodic peak
            peak_cathodic_number (str): Peak number of the cathodic peak
        """
        # Calculate the overpotential for the anodic peak
        self.E_half[cycle][pair]['anodic_overpotential'] =\
            self.anodic_peak_current[cycle][peak_anodic_number]['voltage'] - self.E_half[cycle][pair]['E_half']
        # Calculate the overpotential for the cathodic peak
        self.E_half[cycle][pair]['cathodic_overpotential'] =\
            self.cathodic_peak_current[cycle][peak_cathodic_number]['voltage']  - self.E_half[cycle][pair]['E_half']


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
        cathodic_peak_current = self.cathodic_peak_current[cycle][peak_cathodic_number]["current"]
        cathodic_peak_voltage = self.cathodic_peak_current[cycle][peak_cathodic_number]["voltage"]
        # Smoothen the filtered data
        smoothened_data = filter_cathodic_data.copy()
        smoothened_data["current"] = smoothened_data['current'].rolling(window=self.smoothing_window_size).mean()
        # find the index of the voltage where the current is half of the peak current
        index_of_I_half_voltage = max(filter_cathodic_data.index[filter_cathodic_data['voltage'] >= self.E_half[cycle][pair]['E_half']])
        # find the fitting window size
        fitting_window = int(len(filter_cathodic_data[:index_of_I_half_voltage]) / self.fitting_window_size)

        for i in range(len(smoothened_data.loc[:index_of_I_half_voltage-fitting_window])):
            # select two points and fit a line
            point1, point2 = smoothened_data.iloc[i], smoothened_data.iloc[i+fitting_window]
            # check if the points are not nan
            if (abs(point1["current"]) < abs(point2["current"])) and (point1["voltage"] != point2["voltage"]):
                slope, intercept, _, _, _ = linregress([point1['voltage'], point2['voltage']],
                                                [point1['current'], point2['current']])
                # find the intersection between the line and x = cathodic_peak_voltage in order to find y = I_height
                intersect_y = self._calculate_intersection_updated(slope, intercept, cathodic_peak_voltage)
                if intersect_y > cathodic_peak_current:
                    # calculate the distance between the peak current and the intersection
                    distance_to_peak = abs(cathodic_peak_current) - abs(intersect_y)
                    if distance_to_peak > max_distance:
                        best_point1, best_point2 = point1, point2
                        max_distance = distance_to_peak
                        best_line = (slope, intercept)

        # check if the distance is zero
        if max_distance == 0:
            log.warning(f"No line found for cycle {cycle} and pair {pair} and cathodic peak {peak_cathodic_number}. Increase the smoothing window size or the fitting window size.")
        else:
            # store the height of the peak current
            self.cathodic_peak_current[cycle][peak_cathodic_number]["height"] = max_distance
            self.cathodic_peak_current[cycle][peak_cathodic_number]["capacitative_line"] = best_line


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
        anodic_peak_current = self.anodic_peak_current[cycle][peak_anodic_number]["current"]
        anodic_peak_voltage = self.anodic_peak_current[cycle][peak_anodic_number]["voltage"]
        # Smoothen the filtered data
        filter_anodic_data['current'] = filter_anodic_data['current'].rolling(window=self.smoothing_window_size).mean()
        index_of_I_half_voltage = max(filter_anodic_data.index[filter_anodic_data['voltage'] <= self.E_half[cycle][pair]['E_half']])
        fitting_window = int(len(filter_anodic_data[:index_of_I_half_voltage]) / self.fitting_window_size)

        for i in range(len(filter_anodic_data.loc[:index_of_I_half_voltage-fitting_window])):
            # select two points and fit a line
            point1, point2 = filter_anodic_data.iloc[i], filter_anodic_data.iloc[i+fitting_window]
            if (abs(point1["current"]) > abs(point2["current"])) and (point1["voltage"] != point2["voltage"]):
                slope, intercept, _, _, _ = linregress([point1['voltage'], point2['voltage']],
                                                [point1['current'], point2['current']])

                intersect_y = self._calculate_intersection_updated(slope, intercept, anodic_peak_voltage)
                if intersect_y < anodic_peak_current:
                    distance_to_peak = anodic_peak_current - intersect_y
                    if distance_to_peak > max_distance:
                        best_point1, best_point2 = point1, point2
                        max_distance = distance_to_peak
                        best_line = (slope, intercept)
        if max_distance == 0:
            log.warning(f"No line found for cycle {cycle} and pair {pair} and anodic peak {peak_anodic_number}. Increase the smoothing window size or the fitting window size.")
        else:
            self.anodic_peak_current[cycle][peak_anodic_number]["height"] = max_distance
            self.anodic_peak_current[cycle][peak_anodic_number]["capacitative_line"] = best_line


    def _calculate_intersection_updated(self, line_slope, line_intercept, peak_v):
            """
            Calculate the intersection of the fitted line with the vertical line through the peak.
            The equation of the vertical line is x = peak_i (voltage).
            The equation of the fitted line is y = line_slope * x + line_intercept.
            """
            intersect_i = line_slope * peak_v + line_intercept
            return intersect_i


    def plot(self, save_dir, plots, optional_name: str = None):
        pass


    def save_data(self, save_dir:str, optional_name:str = None):
        pass


    def perform_all_actions(self, save_dir:str, plots:list, optional_name:str = None):
        self.analyze()
        # self.plot(save_dir, plots, optional_name=optional_name)
        #self.save_data(save_dir=save_dir, optional_name=optional_name)
