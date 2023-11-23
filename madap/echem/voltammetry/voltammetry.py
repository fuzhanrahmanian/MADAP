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
