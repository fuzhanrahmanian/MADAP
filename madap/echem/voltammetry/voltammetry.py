from scipy.stats import linregress
from madap.logger import logger
from madap.echem.procedure import EChemProcedure


log = logger.get_logger("voltammetry")

class Voltammetry(EChemProcedure):
    def __init__(self, voltage, current, time,
                 measured_current_units:str,
                 measured_time_units:str,
                 number_of_electrons:str) -> None:
        self.voltage = voltage
        self.current = current
        self.time = time
        self.measured_current_unit = measured_current_units
        self.measured_time_unitis = measured_time_units
        self.number_of_electrons = int(number_of_electrons)
        self.convert_current()
        self.convert_time()

    def convert_current(self):
        """Convert the current to A indipendently from the unit of measure
        """
        if self.measured_current_unit == "uA":
            self.current = self.current * 1e-6
        elif self.measured_current_unit == "mA":
            self.current = self.current * 1e-3
        elif self.measured_current_unit == "A":
            self.current = self.current * 1e0
        else:
            log.error(f"Current unit not supported. Supported units are: uA, mA, A")
            raise ValueError("Current unit not supported")

    def convert_time(self):
        """Convert the time to s indipendently from the unit of measure
        """
        if self.measured_time_unitis == "s":
            self.time = self.time * 1e0
        elif self.measured_time_unitis == "min":
            self.time = self.time * 60
        elif self.measured_time_unitis == "h":
            self.time = self.time * 3600
        elif self.measured_time_unitis == "ms":
            self.time = self.time * 1e-3
        else:
            log.error(f"Time unit not supported. Supported units are: s, min, h")
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

        best_fit = {'start': 0, 'end': self.window_size, 'r_squared': 0, 'slope': 0, 'intercept': 0}
        for start in range(len(x_data) - self.window_size + 1):
            end = start + self.window_size
            slope, intercept, r_value, _, _ = linregress(x_data[start:end], y_data[start:end])
            r_squared = r_value**2
            if r_squared > best_fit['r_squared']:
                best_fit.update({'start': start, 'end': end, 'r_squared': r_squared, 'slope': slope, 'intercept': intercept})
        log.info(f"Best linear fit found from {best_fit['start']} to {best_fit['end']} with R^2 = {best_fit['r_squared']}")
        return best_fit
