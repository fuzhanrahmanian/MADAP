'''Module for GITT measurements'''
from __future__ import annotations
import numpy as np

from attrs import define, field
from attrs.setters import frozen

from madap.logger import logger
from madap.echem.procedure import EChemProcedure
from sklearn.linear_model import LinearRegression
from scipy.optimize import curve_fit
from scipy import stats


log = logger.get_logger("GITT")

@define
class pulse:
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

class pseudo_GITT(EChemProcedure):
    """General GITT class for the analysis of the GITT data.

    Args:
        EChemProcedure (cls): Parent abstract class
    """
    def __init__(self, pulse, vmol:float,numberofcharge:int, contactarea:float):
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
        self.gitttime = pulse.gitttime
        self.gittvoltage = pulse.gittvoltage
        self.gittcurrent = pulse.gittcurrent
        self.vmol = vmol
        self.numberofcharge=numberofcharge
        self.contactarea=contactarea
        self.faraday=96485.3321    #in C/mol

        
    def analyze(self):
        """
        General function for performing the GITT analysis.
        This will do the fits and calculation of the diffusion coefficient.
        """
        ############################################# add self
        coultitration_fit_score = []
        chargevoltage_fit_score = []
        pseudo_diff_list = []

        for i in range(len(gittcurrent)):
            #condition for pulse charge
            if gittcurrent[i][0] > 0.0 or gittcurrent[i][1] > 0.0:
                tempcurrent=[]
                tempvoltlist=[]
                temptimelist=[]
                v_rest = []
                t_rest = []
                for l in range(len(gittcurrent[i])):
                    if gittcurrent[i][l]==0.0:
                        tempcurrent.append(gittcurrent[i][l])
                        tempvoltlist.append(gittvoltage[i][l])
                        temptimelist.append(gitttime[i][l])
                    elif gittcurrent[i][l]!=0.0 and len(temptimelist)>=2:
                        correction = temptimelist[0]
                        for l in range(len(temptimelist)):
                            temp = np.sqrt(temptimelist[l]-correction)
                            temptimelist[l] = temp
                        t_rest.append(temptimelist)
                        v_rest.append(tempvoltlist)
                        tempvoltlist = []
                        temptimelist =[]
                    else:
                        continue

                OCVs = []
                m = -0.3
                c=3.5
                unfitbar_rest = []
                r2valuerest = []
                for m in range(len(t_rest)):
                    try:
                        slope, intercept, r, p, se = stats.linregress(np.array(t_rest[m]), np.array(v_rest[m]))
                        OCVs.append(slope)
                        r2valuerest.append(r**2)
                    except:
                        unfitbar_rest.append(i)
                        OCVs.append(v_rest[m][-1])

                # part for charge fit
                tempcurrent=[]
                tempvoltlist=[]
                temptimelist=[]
                v_charge = []
                t_charge = []
                for n in range(len(gittcurrent[i])):
                    if gittcurrent[i][n]!=0.0:
                        tempcurrent.append(gittcurrent[i][n])
                        tempvoltlist.append(gittvoltage[i][n])
                        temptimelist.append(gitttime[i][n])
                    elif gittcurrent[i][n]==0.0 and len(temptimelist)>=2:
                        correction = temptimelist[0]
                        for u in range(len(temptimelist)):
                            temp = np.sqrt(temptimelist[u]-correction)
                            temptimelist[u] = temp
                        t_charge.append(temptimelist)
                        v_charge.append(tempvoltlist)
                        tempvoltlist = []
                        temptimelist =[]
                    else:
                        continue

                chargeVolt = []
                unfitbar_charge = []
                r2valuecharge = []
                for o in range(len(t_charge)):
                    try:
                        slope, intercept, r, p, se = stats.linregress(np.array(t_charge[o]), np.array(v_charge[o]))
                        chargeVolt.append(slope)
                        r2valuecharge.append(r**2)
                    except:
                        unfitbar_charge.append(o)
                        chargeVolt.append(v_charge[o][-1])
            difflist = []
            current = round(gittcurrent[i][0],3)
            try:
                for p in range(len(OCVs)):
                    diffcoefficient = (4/(np.pi))*((current*vmol)/(contactarea*faraday*chargenumber))**2*(OCVs[p]/chargeVolt[p])**2
                    difflist.append(diffcoefficient)
            except:
                print('Division deltaVsteadystate[i]/voltchange[i] failed see values at '+str(i)+': deltaVsteadystate: '+str(OCVs[i])+'  voltchange: '+str(chargeVolt[i]))
                difflist.append(0)


                """
                Section to extract indices of Pulses.
                """
                pulseindexlist = [] # list with indices of each pulse
                for l in range(len(gittcurrent[i])):
                    if abs(gittcurrent[i][l]-gittcurrent[i][l-1])>0.01 or i ==0:
                        pulseindexlist.append(l)  # safe first value of next on/off part of the pulse
                numberofpulses = len(pulseindexlist)/2
                #log.info(f"Number of pulses calcualted is {numberofpulses}")

                """
                Fitting of steady-state Voltages(here defined as the last voltage value of each pulse).
                Pre slicing data, so we start with on part of pulse necessary.
                """
                regcoulotitration = LinearRegression().fit(points,deltasteadystate_array)
                fit_scorecoulotit = regcoulotitration.score(points, deltasteadystate_array)
                coefficientscoulotit, interceptcoulotit = regcoulotitration.coef_[0], regcoulotitration.intercept_
                
                # save score for later
                coultitration_fit_score.append(fit_scorecoulotit)
                #log.info(f"Fit of coulometric titration curve done with the score {fit_scorecoulotit}")

                """
                Fitting of charge Voltages(here defined as the last voltage value of each pulse) over square root of time.
                Pre slicing data, so we start with on part of pulse necessary.
                """
                chargevoltage = []
                chargesqrttime=[]
                for m in range(0,len(pulseindexlist),2):
                    try:
                        chargevoltage.append(gittvoltage[i][pulseindexlist[m+1]-1]-gittvoltage[i][pulseindexlist[m]])
                        chargesqrttime.append(np.sqrt(gitttime[i][pulseindexlist[m+1]-1]-gitttime[i][pulseindexlist[m]]))
                    except IndexError:
                        continue

                chargevolt_array = np.array(chargevoltage)
                chargesqrttime_array = np.array(chargesqrttime).reshape((-1,1))

                regchargevoltage = LinearRegression().fit(chargesqrttime_array, chargevolt_array)
                fit_scorechargevoltage = regchargevoltage.score(chargesqrttime_array, chargevolt_array)
                coefficientschargevoltage, interceptchargevoltage = regchargevoltage.coef_[0], regchargevoltage.intercept_
                #log.info(f"Fit of charge potentials over square root of time done with the score {fit_scorechargevoltage}")
                
                chargevoltage_fit_score.append(fit_scorechargevoltage)

                pseudo_diff_list.append((4/(np.pi))*((gittcurrent[0]*vmol)/(contactarea*faraday*numberofcharge))**2*(coefficientscoulotit/coefficientschargevoltage)**2)
        

def plot(self, save_dir:str, plots:list, optional_name:str):
        """Abstract method for the plotting of the data.

        Args:
            save_dir (str): The directory where the plots are saved.
            plots (list): The plots that are saved.
            optional_name (str): The optional name of the plot.
        """
        pass
 
def save_data(self, save_dir:str, optional_name:str):
        """Abstract method for the saving of the data.

        Args:
            save_dir (str): The directory where the data is saved.
            optional_name (str): The optional name of the data.
        """
        pass
def perform_all_actions(self, save_dir:str, plots:list, optional_name:str):
        """Abstract method for the performing of all actions.

        Args:
            save_dir (str): The directory where the data is saved.
            plots (list): The plots that are saved.
            optional_name (str): The optional name of the data.
        """
        self.analyze()
        self.plot(save_dir, plots, optional_name=optional_name)
        self.save_data(save_dir=save_dir, optional_name=optional_name)