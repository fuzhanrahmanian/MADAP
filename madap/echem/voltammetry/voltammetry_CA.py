#from madap.echem.voltammetry.voltammetry import Voltammetry
from madap.echem.procedure import EChemProcedure
from madap.logger import logger

log = logger.get_logger("cyclic_amperometry")


class Voltammetry_CA(EChemProcedure):
    def __init__(self, voltage, current, time, active_area=None): #, capacity:list[float]=None) -> None:
        pass
        #super().__init__(voltage, current, time)
        #self.capacity = self._calculate_capacity() if capacity is None else capacity
        #self.cycle = cycle
    def analyze(self):
        pass

    def plot(self):
        # TODO plots
        # TODO i vs t
        # TODO i density vs t
        # TODO Q vs t
        # TODO i vs t^(-0.5)
        # TODO Q vs time^(0.5)
        pass

    def save_data(self):
        pass

    def perform_all_actions(self, result_dir, plots):
        pass

    def _calculate_capacity(self):
        # TODO di/dt
        pass