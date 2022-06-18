import os, time
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
from madap import logger

log = logger.get_logger("plotting")
class Plots():
    def __init__(self) -> None:

        mpl.rcParams.update(mpl.rcParamsDefault)
        mpl.rc('font', size=20)
        mpl.rc('axes', titlesize=20)
        plt.style.use(['nature', 'science', 'no-latex'])
        plt.rcParams['text.usetex'] = False
        plt.rcParams['xtick.direction'] = 'in'
        plt.rcParams['ytick.direction'] = 'in'

    def plot_identity(self, ax, xlabel:str=None, ylabel:str=None, x_lim:list=None, y_lim:list=None, rotation:float=0):
        if xlabel:
            ax.set_xlabel(xlabel, fontsize=12)
        if ylabel:
            ax.set_ylabel(ylabel, fontsize=12)
        if x_lim:
            ax.set_xlim([min(x_lim), max(x_lim)])
            ax.set_xticks(np.arange(min(x_lim), max(x_lim), max(x_lim)/5))
        if y_lim:
            ax.set_ylim([min(y_lim), max(y_lim)])
            ax.set_yticks(np.arange(min(y_lim), max(y_lim), max(y_lim)/5))
        if rotation:
            ax.xaxis.set_tick_params(rotation=rotation)

    def add_colorbar(self, plot, ax, scientific_label=None):

            cb = plt.colorbar(plot, ax=ax)

            if scientific_label:
                cb.formatter.set_powerlimits((scientific_label, scientific_label))
                cb.update_ticks()

    def compose_subplot():
        pass

    def save_plot(self, fig, directory, name):
        log.info(f"Saving .png and .svg in {directory}")
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        name = f"{timestamp}_{name}"
        fig.savefig(os.path.join(directory, f"{name}.svg"), dpi=900)
        fig.savefig(os.path.join(directory, f"{name}.png"), dpi=900)