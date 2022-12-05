"""Cyclic Potentiometry Analysis module."""
from attrs import define, field
from attrs.setters import frozen
from madap.echem.procedure import EChemProcedure
from madap.logger import logger

log = logger.get_logger("cyclic_potentiometry")

@define
class Voltammetry_CP(EChemProcedure):
    """Class for data definition that will be used during the galvanostatic Cyclic Potentiometric analysis.
       The data includes the following: voltage, time, current, loading and charge.
    """
    voltage: list[float] = field(on_setattr=frozen)  # [V]
    time: list[float] = field(on_setattr=frozen)     # [s]
    current: float = field(on_setattr=frozen)        # [A]
    loading: float = field(default=None)             # [gr]
    charge = None

    def __repr__(self) -> str:
        """Return the string representation of the object."""
        return f"Voltammetry_CP(voltage={self.voltage}, time={self.time}, current={self.current},\
            loading={self.loading})"

    def analyze(self):
        pass


    def plot(self, save_dir, plots, optional_name: str = None):
        # TODO V vs t
        # TODO V vs Q or V vs C
        # TODO dQ/dV vs V or dC/dV vs V
        pass


    def save_data(self, save_dir, optional_name: str = None):
        pass


    def perform_all_actions(self, save_dir, plots : list, optional_name: str = None):
        """Wrapper function for executing all the actions that are needed to be performed on the data.

        Args:
            save_dir (str): Directory where the data should be saved.
            plots (list): List of plots that should be generated.
            optional_name (str, optional): Optional name for the file. Defaults to None.
        """


    def _calculate_charge(self):
        self.charge = self.current * self.time

