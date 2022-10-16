import os
from attrs import define, field
from attrs.setters import frozen
from madap.logger import logger
from madap.echem.procedure import EChemProcedure


log = logger.get_logger("voltammetry")

@define
class Voltammetry(EChemProcedure):
    voltage = field(default=0)
    current = field(default=0)
    time = field(default=0)

    def _calculate_capacity(self):
        # TODO di/dt
        pass

    def _calculate_columbic_efficiency(self):
        # TODO
        pass