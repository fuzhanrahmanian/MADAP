'''Module for GITT measurements'''

import numpy as np

from attrs import define, field
from attrs.setters import frozen

from madap.logger import logger
from madap.echem.procedure import EChemProcedure

from __future__ import annotations

log = logger.get_logger("GITT")

@define
class GITT:
    """Class for data definition that will be used during the GITT analysis.
        The data includes the following: time, current, voltage. .
    """
    gitttime : list[float] = field(on_setattr=frozen)
    gittcurrent : list[float] = field(on_setattr=frozen)
    gittvoltage : list[float] = field( on_setattr=frozen)

    def __repr__(self) -> str:
        """Returns a string representation of the object."""
        return f"Impedance(frequency={self.frequency}, real_impedance={self.real_impedance}, \
                imaginary_impedance={self.imaginary_impedance}, phase_shift={self.phase_shift})"

class GITT(EChemProcedure):
    """General GITT class for the analysis of the GITT data.

    Args:
        EChemProcedure (cls): Parent abstract class
    """
    def __init__(self, gitttime, gittvoltage,gittcurrent, vmol:float,numberofcharge:int, contactarea:float, faraday:float =96485.3321233100184):
        """ Initialize the GITT class.

        Args:
            gitttime (float,np.array): Time(s) data of the GITT measurement.
            gittvoltage (float, np.array): Voltage of the GITT measurement.
            gittcurrent(float,np.array): Current of the GITT measurement.
            vmol(float): Molar volume of the electrode in cm^3/mol.
            numberofcharge(int): Chargenumber of the intercalating species.
            contactarea(float): Contact area of the electrode with the electrolyte in cm^2.
            faraday(float): Faraday constant in C/mo.
        """
        self.gitttime = gitttime
        self.gittvoltage = gittvoltage
        self.gittcurrent = gittcurrent
        self.vmol = vmol
        self.numberofcharge=numberofcharge
        self.contactarea=contactarea
        self.faraday=faraday

    def analyze(self):
        """
        General function for performing the GITT analysis.
        This will do the fits and calculation of the diffusion coefficient.
        """

        """
        Section to extract indices of Pulses.
        """
        pulseindexlist = [] # list with indieces of each pulse
        for i in range(len(self.gittcurrent)):
            if self.gittcurrent[i] != self.gittcurrent[i-1] and i > 0:
                pulseindexlist.append(i)
        numberofpulses = len(pulseindexlist)/2


