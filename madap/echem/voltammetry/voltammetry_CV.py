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
        self.data = None

    def analyze(self):

        # create a dataframe from self.scan_rate and self.np_time, self.np_current, self.np_voltage
        self.data = pd.DataFrame({'scan_rate': self.scan_rate, 'time': self.np_time,
                           'current': self.np_current, 'voltage': self.np_voltage})
        # Identify forward and backward scans
        self._find_fwd_bwd_scans()
        # Identify cycles
        self._identify_cycles()
        # todo: find the cycle number
        # todo: find the peak current for both anodic and cathodic peak
        # todo: find the potential at the peak current and calculate the E_half
        # todo: find the height of the peak current to the linearly fitted baseline
        # todo: find the capacitative and faradaic current
        # todo: calculate the diffucsion coefficient from Randles Scelvik equation
        # todo: get the two linear lines from Tafel plot and calculate the E_corr and I_corr
        # todo: calculate the capactiy of the electrode
        # call a function that
        # separate all the cycles
        # self._find_fwd_and_bkw_scans()
        self._find_peak_currents()



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
