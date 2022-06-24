import os
from attrs import define, field
from attrs.setters import frozen
from madap import logger
from echem.procedure import EChemProcedure


log = logger.get_logger("voltammetry")

@define
class Voltammetry(EChemProcedure):
    voltage = field(default=0)
    current = field(default=0)
    time = field(default=0)
