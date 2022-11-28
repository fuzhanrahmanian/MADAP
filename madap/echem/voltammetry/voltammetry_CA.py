#adds by leon
from __future__ import annotations

from madap.echem.voltammetry.voltammetry import Voltammetry
from madap.echem.procedure import EChemProcedure
from madap.logger import logger

log = logger.get_logger("cyclic_amperometry")


class Voltammetry_CA(Voltammetry, EChemProcedure):
    def __init__(self, voltage, current, time, capacity:list[float]=None, cycle=None) -> None:
        super().__init__(voltage, current, time)
        self.capacity = self._calculate_capacity() if capacity is None else capacity
        self.cycle = cycle
    def analyze(self):
        pass

    def plot(self):
        # TODO plots
        # TODO i vs t
        # TODO i vs Q
        # TODO currentDensity vs time
        # TODO Q vs cycle
        pass

    def save_data(self):
        pass

    def perform_all_actions(self, result_dir, plots):
        pass

    def _calculate_capacity(self):
        # TODO di/dt
        pass