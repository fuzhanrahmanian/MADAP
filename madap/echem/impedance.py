

# stuff that should go her

from re import I

# todo: make an abstract class out of this
class EIS(plot, data): # plot and data of our defined classes maybe open a folder calls "util" and we can call it from there. There data will be assembled, new directories can be created, dataframe can be built.
                       # from plot we will import the plot styles, colots, type, subplots, colot bar , legend ... maybe learn the kwargs**
    def __init__(self, frequency, real_impedance, imaginary_impedance) -> None:
        self.frequency = frequency
        self.real_impedance = real_impedance
        self.imaginary_impedance = imaginary_impedance
        self.phase_shift => optional
        # logging info to show the what we gave
        def nyquist_plot():pass
        def bode_plot(): pass
        def fit_eis(): pass # with randles, custom or used the predefined one, give the equivalent circuit and its paramteres (optinional save or not)
        def prediifined_circuits(): pass # maybe push this somewhere else , in something like config or so
        def plot_real_measured(): pass # draw fitted versus real in byquist plot and draw the circuit on the side
        def validity_fit():pass # get the residuals, chi square of real , imaginary and both # show consistency and over/under fit
        def plot_residual(): pass # should be part of validity
        def llissajous_plot(): pass # show the linearity V-I , v vs time and i vs time , stability , and casuality and stability
        def analsys_eis(): pass # all the functionions except lissajous