'''Module for GITT measurements'''

import numpy as np

from attrs import define, field
from attrs.setters import frozen

from madap.logger import logger
from madap.echem.procedure import EChemProcedure
from sklearn.linear_model import LinearRegression

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
    def __init__(self, gitttime, gittvoltage,gittcurrent, vmol:float,numberofcharge:int, contactarea:float):
        """ Initialize the GITT class.

        Args:
            gitttime (float,np.array): Time(s) data of the GITT measurement.
            gittvoltage (float, np.array): Voltage of the GITT measurement.
            gittcurrent(float,np.array): Current of the GITT measurement.
            vmol(float): Molar volume of the electrode in cm^3/mol.
            numberofcharge(int): Charge number of the intercalating species.
            contactarea(float): Contact area of the electrode with the electrolyte in cm^2.
            faraday(float): Faraday constant in C/mol.
        """
        self.gitttime = gitttime
        self.gittvoltage = gittvoltage
        self.gittcurrent = gittcurrent
        self.vmol = vmol
        self.numberofcharge=numberofcharge
        self.contactarea=contactarea
        self.faraday=96485.3321    #in C/mol

        
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
            if self.gittcurrent[i] != self.gittcurrent[i-1] or i ==0:
                pulseindexlist.append(i)  # safe first value of next on/off part of the pulse
        numberofpulses = len(pulseindexlist)/2
        log.info(f"Number of pulses calcualted is {numberofpulses}")

        """
        Fitting of steady-state Voltages(here defined as the last voltage value of each pulse).
        Pre slicing data, so we start with on part of pulse necessary.
        """
        steadystatevoltage = []

        for i in range(1,len(pulseindexlist),2):
            steadystatevoltage.append(self.gittvoltage[pulseindexlist[i]-1])
        
        deltasteadystatevoltage = []
        for o in range(1,len(steadystatevoltage)):
                deltasteadystatevoltage.append(steadystatevoltage[o]-steadystatevoltage[o-1])
        
        regcoulotitration = LinearRegression().fit(np.linspace(1,len(deltasteadystatevoltage), len(deltasteadystatevoltage)), deltasteadystatevoltage)
        self.fit_scorecoulotit = regcoulotitration.score(np.linspace(1,len(deltasteadystatevoltage), len(deltasteadystatevoltage)), deltasteadystatevoltage)
        self.coefficientscoulotit, self.interceptcoulotit = regcoulotitration.coef_[0], regcoulotitration.intercept_

        log.info(f"Fit of coulometric titration curve done with the score {self.fit_scorecoulotit}")

        """
        Fitting of charge Voltages(here defined as the last voltage value of each pulse) over square root of time.
        Pre slicing data, so we start with on part of pulse necessary.
        """
        chargevoltage = []
        chargesqrttime=[]
        for i in range(0,len(pulseindexlist),2):
            chargevoltage.append(self.gittvoltage[pulseindexlist[i+1]-1]-self.gittvoltage[pulseindexlist[i]])
            chargesqrttime.append(np.sqrt(self.gitttime[pulseindexlist[i+1]-1]-self.gitttime[pulseindexlist[i]]))

        regchargevoltage = LinearRegression().fit(chargesqrttime, chargevoltage)
        self.fit_scorechargevoltage = regchargevoltage.score(chargesqrttime, chargevoltage)
        self.coefficientschargevoltage, self.interceptchargevoltage = regchargevoltage.coef_[0], regchargevoltage.intercept_
        log.info(f"Fit of charge potentials over square root of time done with the score {self.fit_scorechargevoltage}")

        diffcoefficient = (4/(np.pi))*((self.gittcurrent[0]*self.vmol)/(self.contactarea*self.faraday*self.numberofcharge))**2*(self.coefficientscoulotit/self.coefficientschargevoltage)**2
        


def plot(self, save_dir:str, plots:list, optional_name:str):
        """Abstract method for the plotting of the data.

        Args:
            save_dir (str): The directory where the plots are saved.
            plots (list): The plots that are saved.
            optional_name (str): The optional name of the plot.
        """
 
def save_data(self, save_dir:str, optional_name:str):
        """Abstract method for the saving of the data.

        Args:
            save_dir (str): The directory where the data is saved.
            optional_name (str): The optional name of the data.
        """
def perform_all_actions(self, save_dir:str, plots:list, optional_name:str):
        """Abstract method for the performing of all actions.

        Args:
            save_dir (str): The directory where the data is saved.
            plots (list): The plots that are saved.
            optional_name (str): The optional name of the data.
        """