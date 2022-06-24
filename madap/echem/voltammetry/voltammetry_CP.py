from madap.echem.voltammetry.voltammetry import Voltammetry
from madap.echem.procedure import EChemProcedure
from madap import logger

log = logger.get_logger("cyclic_potentiometry")


class Voltammetry_CP(Voltammetry, EChemProcedure):
    def __init__(self, voltage, current, time) -> None:
        super().__init__(voltage, current, time)

    def analyze():
        pass

    def plot():
        # TODO V vs t
        # TODO dQ vs dV
        # TODO v vs Q
        pass

    def save_data():
        pass

    def perform_all_actions():
        pass
