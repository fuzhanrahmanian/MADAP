from madap.echem.voltammetry.voltammetry import Voltammetry
from madap.echem.procedure import EChemProcedure
from madap.logger import logger

log = logger.get_logger("cyclic_voltammetry")


class Voltammetry_CV(Voltammetry, EChemProcedure):
    def __init__(self, voltage, current, time) -> None:
        super().__init__(voltage, current, time)

    def analyze():
        # TODO
        pass

    def plot():
        # TODO plots
        # TODO V vs I
        pass

    def save_data():
        pass

    def perform_all_actions():
        pass
    def _peek_to_peek_seperation(self):
        pass
    def _calcualte_diffusion_coefficient(self):
        pass
    def _randles_sevcik_equation(self):
        pass