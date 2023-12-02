import numpy as np
import pandas as pd
from scipy.signal import find_peaks
from madap.echem.voltammetry.voltammetry import Voltammetry
from madap.echem.procedure import EChemProcedure
from madap.logger import logger


log = logger.get_logger("cyclic_voltammetry")


class Voltammetry_CV(Voltammetry, EChemProcedure):
    def __init__(self, current, voltage, time, args, scan_rate=None) -> None:
        super().__init__(voltage, current, time, args=args)
        self.scan_rate = np.array(scan_rate) if scan_rate is not None else None
        self.cycle_indexes = []
        self.cycle_data = {}
        self.forward_scan = {}
        self.backward_scan = {}
        self.direction_index = {}
        self.anodic_peak_current = {}
        self.cathodic_peak_current = {}
        self.E_half = {}
        self.data = None
        self.width = 15 if args.peak_width is None else int(args.peak_width)
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
        self._calculate_diffusion_coefficient()
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
        max_voltage = np.max(self.np_voltage)
        min_voltage = np.min(self.np_voltage)
        scan_directions = []

        for voltage in self.np_voltage:
            # Check if the voltage has reached its extremum and switch direction
            if (direction == 'F' and voltage >= max_voltage) or (direction == 'B' and voltage <= min_voltage):
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
        """ Find the peak currents in the data.
        """
        # Iterate through each cycle and direction
        for cycle in self.data['cycle_number'].unique():
            for direction in ['F', 'B']:
                # Filter the data for the current cycle and direction
                cycle_data = self.data[(self.data['cycle_number'] == cycle) & (self.data['scan_direction'] == direction)]

                # Identify peaks
                if direction == 'F':  # Forward scan - looking for cathodic peaks
                    peaks, _ = find_peaks(cycle_data['current'], width=self.width)
                    self._store_peak_data(peaks=peaks, data=cycle_data, cycle_num=cycle, peak_type='cathodic', scan_direction=direction)
                else:  # Backward scan - looking for anodic peaks
                    peaks, _ = find_peaks(-cycle_data['current'], width=self.width)
                    self._store_peak_data(peaks=peaks, data=cycle_data, cycle_num=cycle, peak_type='anodic', scan_direction=direction)


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

        for peak in peaks:
            peak_data = {
                'current': data.iloc[peak]['current'],
                'voltage': data.iloc[peak]['voltage'],
                'index': data.index[peak],
                'cycle_num': cycle_num,
                'direction': scan_direction,
                'peak_type': 'cathodic' if peak_type == 'cathodic' else 'anodic',
                'scan_rate': data.iloc[peak]['scan_rate']}
            peak_dict[f'peak_{len(peak_dict) + 1}'] = peak_data


    def _calculate_E_half(self):
        """ Calculate the half-wave potential for each anodic peak."""
        for anodic_key, anodic_peak in self.anodic_peak_current.items():
            closest_cathodic_peak = None
            min_current_difference = float('inf')

            for _ , cathodic_peak in self.cathodic_peak_current.items():
                current_difference = abs(anodic_peak['current'] - cathodic_peak['current'])

                if current_difference < min_current_difference:
                    min_current_difference = current_difference
                    closest_cathodic_peak = cathodic_peak

            if closest_cathodic_peak:
                average_voltage = (anodic_peak['voltage'] + closest_cathodic_peak['voltage']) / 2
                self.E_half[anodic_key] = {
                    'anodic_peak': anodic_key,
                    'cathodic_peak': closest_cathodic_peak['index'],
                    'E_half': average_voltage
                }

        # Check if there are any unmatched peaks
        if not self.E_half:
            log.info("No matching current pairs found for E_half calculation.")


    def _calculate_diffusion_coefficient(self):
        # Constants
        const_298K = 2.69 * 10**5
        const_other_temp = 0.4463

        # Function to calculate D
        def calculate_D(i_peak, scan_rate):
            if int(self.temperature) == 298:
                # Randles-Sevcik equation
                #i_peak [A] = 2.69 * 10**5 * n**(3/2) * A * C * v**(1/2) * D**(1/2) with A [cm^2], C [mol/cm^3], v [V/s], D [cm^2/s]
                denominator = (const_298K * self.number_of_electrons**(3/2) * self.electrode_area * self.concentration_of_active_material * (scan_rate**0.5))
                return (i_peak / denominator)**2
            else:
                # Randles-Sevcik equation
                #i_peak [A] = 0.4463 * n * F * A * C * (n**(1/2) * v**(1/2) * D**(1/2)/R*T)**(1/2) with A [cm^2], C [mol/cm^3], v [V/s], D [cm^2/s]
                coefficient = ((self.number_of_electrons * self.faraday_constant * scan_rate)/(self.gas_constant * self.temperature))**0.5
                denominator =  (const_other_temp * self.number_of_electrons * self.faraday_constant * self.electrode_area * self.concentration_of_active_material * coefficient)
                return (i_peak / denominator)**2

        # Find the highest peak in anodic and cathodic direction
        highest_anodic_peak_key = max(self.anodic_peak_current, key=lambda k: self.anodic_peak_current[k]['current'])
        highest_cathodic_peak_key = max(self.cathodic_peak_current, key=lambda k: self.cathodic_peak_current[k]['current'])


        # Calculate D for anodic and cathodic peaks
        D_anodic = calculate_D(self.anodic_peak_current[highest_anodic_peak_key]['current'], self.anodic_peak_current[highest_anodic_peak_key]['scan_rate'])
        D_cathodic = calculate_D(self.cathodic_peak_current[highest_cathodic_peak_key]['current'], self.cathodic_peak_current[highest_cathodic_peak_key]['scan_rate'])

        # Add D to the peak dictionaries
        self.anodic_peak_current[highest_anodic_peak_key]['D'] = D_anodic
        self.cathodic_peak_current[highest_cathodic_peak_key]['D'] = D_cathodic


    def plot(self, save_dir, plots, optional_name: str = None):
        pass

    def save_data(self, save_dir:str, optional_name:str = None):
        pass

    def perform_all_actions(self, save_dir:str, plots:list, optional_name:str = None):
        self.analyze()
        self.plot(save_dir, plots, optional_name=optional_name)
        #self.save_data(save_dir=save_dir, optional_name=optional_name)

    def _peek_to_peek_seperation(self):
        pass
    def _calcualte_diffusion_coefficient(self):
        pass
    def _randles_sevcik_equation(self):
        pass