"""Cyclic Potentiometry Analysis module."""
from attrs import define, field
from attrs.setters import frozen
#from madap.echem.voltammetry.voltammetry import Voltammetry
from madap.echem.procedure import EChemProcedure
from madap.logger import logger

log = logger.get_logger("cyclic_potentiometry")

@define
class Voltammetry_CP(EChemProcedure):
    def __init__(self, voltage: list, time: list, current: float, loading: float = None):
        voltage: list[float] = field(on_setattr=frozen)  # [V]
        time: list[float] = field(on_setattr=frozen)     # [s]
        current: float = field(on_setattr=frozen)        # [A]
        loading: float = field(default=None)             # [gr]
        charge = None

    def analyze(self):
        pass

    def plot(self):
        # TODO V vs t
        # TODO dQ vs dV
        # TODO v vs Q
        pass

    def save_data(self):
        pass

    def perform_all_actions(self):
        pass
    def _calculate_charge(self):
        self.charge = self.current * self.time

