""" This module handels the general plotting functions for the MADAP application. """
import os
import math

import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl

from madap.logger import logger


mpl.use('svg')
log = logger.get_logger("plotting")
class Plots():
    """_General class for multipurpose plotting
    """
    def __init__(self) -> None:

        mpl.rcParams.update(mpl.rcParamsDefault)
        mpl.rc('font', size=20)
        mpl.rc('axes', titlesize=20)
        style_path, _ =os.path.split(__file__)
        plt.style.use([os.path.join(style_path, 'styles', 'nature.mplstyle'),
                       os.path.join(style_path, 'styles', 'science.mplstyle'),
                       os.path.join(style_path, 'styles', 'no-latex.mplstyle')])
        plt.rcParams['text.usetex'] = False
        plt.rcParams['xtick.direction'] = 'in'
        plt.rcParams['ytick.direction'] = 'in'
        self.plot_type = ""
        self.ax = None

    def plot_identity(self, ax, xlabel:str=None, ylabel:str=None, x_lim:list=None, y_lim:list=None,
                      rotation:float=0, ax_sci_notation:bool=False, scientific_limit=0,
                      log_scale:str=None, step_size_x="auto", step_size_y="auto"):
        """Defines the "identity" of the plot.
        This includes the x and y labels, the x and y limits, the rotation of the x labels,
        wether or not scientific notation should be used,
        the log scale and the step size of the x and y axis.

        Args:
            ax (matplotlib.axes): axis to which the identity line should be added
            xlabel (str, optional): label of the x-axis. Defaults to None.
            ylabel (str, optional): label of the y-axis. Defaults to None.
            x_lim (list, optional): limits of the x-axis. Defaults to None.
            y_lim (list, optional): limits of the y-axis. Defaults to None.
            rotation (float, optional): rotation of the x and ylabels. Defaults to 0.
            ax_sci_notation (bool, optional): whether or not scientific notation should be used.
            scientific_limit (int, optional): scientific notation limit. Defaults to 0.
            log_scale (str, optional): log scale of the x and y axis. Defaults to None.
            Can be "x", "y"
            base10 (bool, optional): base 10 log scale. Defaults to False.
            step_size_x (str, optional): step size of the x axis. Defaults to "auto".
            step_size_y (str, optional): step size of the y axis. Defaults to "auto".
        """
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
            ax.ticklabel_format(style='sci', axis=ax_sci_notation, \
                                scilimits=(scientific_limit, scientific_limit))
        if log_scale:
            ax.set_xscale('log') if log_scale=='x' else (ax.set_yscale('log') if log_scale=='y' else (ax.set_xscale('log'), ax.set_yscale('log')))


    def add_colorbar(self, plot, ax, scientific_label_colorbar=None, scientific_limit=3, colorbar_label=None):
        """Adds a colorbar to a plot

        Args:
            plot (matplotlib.pyplot): plot to which the colorbar should be added
            ax (matplotlib.axes): axis to which the colorbar should be added
            scientific_label_colorbar (str, optional): whether or not the colorbar should be written
            scientific_limit (int, optional): scientific notation limit. Defaults to 3.
            colorbar_label (str, optional): label of the colorbar. Defaults to None.
        """

        color_bar = plt.colorbar(plot, ax=ax)

        if colorbar_label:
            color_bar.set_label(colorbar_label, fontsize=7)
            color_bar.ax.yaxis.set_label_position('right')


        if scientific_label_colorbar:
            color_bar.formatter.set_powerlimits((scientific_limit, scientific_limit))
            color_bar.update_ticks()

    def round_hundredth(self, nums):
        """Rounds a number to the nearest hundredth

        Args:
            nums (float): number to be rounded

        Returns:
            float: rounded number
        """
        if not nums.all() < 0:
            min_num, max_num = int(math.ceil(min(nums) / 100.0)) * 100 - 100, \
                int(math.ceil(max(nums) / 100.0)) * 100
        else:
            min_num, max_num = int(math.ceil(min(nums) / 100.0)) * 100 , \
                int(math.ceil(max(nums) / 100.0)) * 100+ 100
        return min_num, max_num

    def round_tenth(self, nums):
        """Rounds a number to the nearest tenth

        Args:
            nums (float): number to be rounded

        Returns:
            float: rounded number
        """
        if not nums.all() < 0:
            min_num, max_num = round(min(nums), -1) - 10, round(max(nums), -1)
        else:
            min_num, max_num = round(min(nums), -1) , round(max(nums), -1) + 10
        return min_num, max_num

    def set_xtick_for_two_axes(self, ax1, ax2, ax1_ticks, ax2_ticks, invert_axes=False):
        """Sets the xticks for two axes

        Args:
            ax1 (matplotlib.axes): first axis
            ax2 (matplotlib.axes): second axis
            ax1_ticks (list): ticks for the first axis
            ax2_ticks (list): ticks for the second axis
            invert_axes (bool, optional): whether or not the axes should be inverted. Default False.
        """
        ax1.set_xlim(ax2.get_xlim())
        ax1.set_xticks(ax2_ticks)
        ax1.set_xticklabels(ax1_ticks)
        if invert_axes:
            ax1.invert_xaxis()
            ax2.invert_xaxis()

    def save_plot(self, fig, directory, name):
        """Saves a plot

        Args:
            fig (matplotlib.pyplot): figure to be saved
            directory (str): directory in which the plot should be saved
            name (str): name of the plot
        """
        log.info(f"Saving .png and .svg in {directory}")
        fig.savefig(os.path.join(directory, f"{name}.svg"), dpi=900)
        fig.savefig(os.path.join(directory, f"{name}.png"), dpi=900)
