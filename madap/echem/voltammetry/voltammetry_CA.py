#from madap.echem.voltammetry.voltammetry import Voltammetry
from madap.echem.procedure import EChemProcedure
from madap.logger import logger

log = logger.get_logger("cyclic_amperometry")


class Voltammetry_CA(EChemProcedure):
    def __init__(self,current: list, time: list, voltage: float, active_area: float=None): #, capacity:list[float]=None) -> None:
        self.voltage = voltage
        self.current = current
        self.time = time
        self.active_area = active_area

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