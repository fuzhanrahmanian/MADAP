import os, time
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
from madap import logger
from matplotlib.axes import Axes
import math

log = logger.get_logger("plotting")
class Plots():
    """_General class for multipurpose plotting
    """
    def __init__(self) -> None:

        mpl.rcParams.update(mpl.rcParamsDefault)
        mpl.rc('font', size=20)
        mpl.rc('axes', titlesize=20)
        plt.style.use(['nature', 'science', 'no-latex'])
        plt.rcParams['text.usetex'] = False
        plt.rcParams['xtick.direction'] = 'in'
        plt.rcParams['ytick.direction'] = 'in'

    def plot_identity(self, ax, xlabel:str=None, ylabel:str=None, x_lim:list=None, y_lim:list=None, rotation:float=0,
                      ax_sci_notation=None, scientific_limit=0, log_scale=None, base10:bool=False, 
                      step_size_x="auto", step_size_y="auto"):
        # ax_sci_notation (str, optiopnal): whether or not an axis should be written with
        #         scientific notation. It can be 'x', 'y', 'both' or None.
        if xlabel:
            ax.set_xlabel(xlabel, fontsize=9)
        if ylabel:
            ax.set_ylabel(ylabel, fontsize=9)
        if x_lim:
            step = (max(x_lim)-min(x_lim))/5 if step_size_x=="auto" else step_size_x
            ax.set_xlim([min(x_lim), max(x_lim)])
            ax.set_xticks(np.arange(min(x_lim), max(x_lim), step))
        if y_lim:
            step = (max(y_lim)-min(y_lim))/5 if step_size_y=="auto" else step_size_y
            ax.set_ylim([min(y_lim), max(y_lim)])
            ax.set_yticks(np.arange(min(y_lim), max(y_lim), step))
        if rotation:
            ax.xaxis.set_tick_params(rotation=rotation)
        if ax_sci_notation:
            ax.ticklabel_format(style='sci', axis=ax_sci_notation, scilimits=(scientific_limit, scientific_limit))
        if log_scale:
            ax.set_xscale('log') if log_scale=='x' else (ax.set_yscale('log') if log_scale=='y' else (ax.set_xscale('log'), ax.set_yscale('log')))


    def add_colorbar(self, plot, ax, scientific_label_colorbar=None, scientific_limit=3, colorbar_label=None):
            # add label to colorbar

            cb = plt.colorbar(plot, ax=ax)

            if colorbar_label:
                cb.set_label(colorbar_label, fontsize=7)
                cb.ax.yaxis.set_label_position('right')


            if scientific_label_colorbar:
                cb.formatter.set_powerlimits((scientific_limit, scientific_limit))
                cb.update_ticks()

    def round_hundredth(self, nums):
        if not nums.all() < 0:
            min_num, max_num = int(math.ceil(min(nums) / 100.0)) * 100 - 100, int(math.ceil(max(nums) / 100.0)) * 100
        else:
            min_num, max_num = int(math.ceil(min(nums) / 100.0)) * 100 , int(math.ceil(max(nums) / 100.0)) * 100+ 100
        return min_num, max_num

    def round_tenth(self, nums):
        if not nums.all() < 0:
            min_num, max_num = round(min(nums), -1) - 10, round(max(nums), -1)
        else:
            min_num, max_num = round(min(nums), -1) , round(max(nums), -1) + 10
        return min_num, max_num

    def set_xtick_for_two_axes(self, ax1, ax2, ax1_ticks, ax2_ticks, invert_axes=False):
        ax1.set_xlim(ax2.get_xlim())
        ax1.set_xticks(ax2_ticks)
        ax1.set_xticklabels(ax1_ticks)
        if invert_axes:
            ax1.invert_xaxis()
            ax2.invert_xaxis()

    def compose_subplot():
        pass

    def save_plot(self, fig, directory, name):
        log.info(f"Saving .png and .svg in {directory}")
        fig.savefig(os.path.join(directory, f"{name}.svg"), dpi=900)
        fig.savefig(os.path.join(directory, f"{name}.png"), dpi=900)