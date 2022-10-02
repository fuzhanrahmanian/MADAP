"""Impedance Plotting module."""
import numpy as np
import matplotlib.colors as mcl
from matplotlib import pyplot as plt
from matplotlib.lines import Line2D

from madap.logger import logger
from madap.plotting.plotting import Plots


log = logger.get_logger("impedance_plotting")

class ImpedancePlotting(Plots):
    """General Plotting class for Impedance method.

    Args:
        Plots (class): Parent class for plotting all methods.
    """
    def __init__(self) -> None:
        super().__init__()
        self.plot_type = "impedance"

    def nyquist(self, subplot_ax, frequency, real_impedance, imaginary_impedance,
                colorbar:bool=True, ax_sci_notation = None, scientific_limit=None,
                scientific_label_colorbar=False, legend_label=False,voltage:float = None,
                color_map:str="viridis", norm_color=None):
        """Defines the nyquist plot for raw data

        Args:
            subplot_ax (ax): Subplot axis
            frequency (np.array): Frequency array.
            real_impedance (np.array): Real impedance array.
            imaginary_impedance (np.array): Imaginary impedance array.
            colorbar (bool, optional): If True, adds a colorbar. Defaults to True.
            ax_sci_notation (bool, optional): If True, adds scientific notation to the axis. Defaults to None.
            scientific_limit (int, optional): If ax_sci_notation is True, defines the number of significant digits. Defaults to None.
            scientific_label_colorbar (bool, optional): If True, adds scientific notation to the colorbar. Defaults to False.
            legend_label (bool, optional): If True, adds a legend. Defaults to False.
            voltage (float, optional): Voltage of the circuit. Defaults to None.
            color_map (str, optional): Color map. Defaults to "viridis".
            norm_color (bool, optional): If True, normalizes the colorbar. Defaults to None.
        """

        log.info("Creating Nyquist plot")
        norm = mcl.LogNorm(vmin=min(frequency), vmax=max(frequency)) if norm_color else None

        label = f"v = {voltage} [V]" if (voltage and voltage != "")  else None
        nyquist_plot = subplot_ax.scatter(real_impedance, -imaginary_impedance,
                                          c=frequency, norm=norm, s=10,
                                          cmap=color_map, rasterized=True,
                                          label=label)

        nyquist_plot.set_clim(min(frequency), max(frequency))

        self.plot_identity(subplot_ax, xlabel=r"Z' $[\Omega]$", ylabel=r"-Z'' $[\Omega]$",
                            x_lim=[0, max(real_impedance)+200],
                            y_lim=[0, max(-imaginary_impedance)+200],
                            ax_sci_notation=ax_sci_notation,
                            scientific_limit=scientific_limit)

        if (legend_label and voltage is not None):
            _, labels = subplot_ax.get_legend_handles_labels()
            new_handles= [Line2D([0], [0], marker='o',
                        markerfacecolor="black",
                        markeredgecolor="black", markersize=3, ls='')]
            subplot_ax.legend(new_handles, labels, loc="upper left",fontsize=5.5)

        if colorbar:
            self.add_colorbar(nyquist_plot, subplot_ax, scientific_label_colorbar,
                            scientific_limit=scientific_limit,
                            colorbar_label=r"f $[Hz]$")

    def bode(self, subplot_ax, frequency, real_impedance, imaginary_impedance, phase_shift,
             ax_sci_notation=None, scientific_limit=None, log_scale='x'):
        """Defines the bode plot for raw data

        Args:
            subplot_ax (ax): Subplot axis
            frequency (np.array): Frequency array.
            real_impedance (np.array): Real impedance array.
            imaginary_impedance (np.array): Imaginary impedance array.
            phase_shift (np.array): Phase shift array.
            ax_sci_notation (bool, optional): If True, adds scientific notation to the axis. Defaults to None.
            scientific_limit (int, optional): If ax_sci_notation is True, defines the number of significant digits. Defaults to None.
            log_scale (str, optional): If 'x', plots the x axis in log scale. Defaults to 'x'.
        """
        log.info("Creating Bode plot")
        impedance_magnitude = np.sqrt(real_impedance**2 +  imaginary_impedance**2)
        subplot_ax.scatter(frequency, impedance_magnitude, rasterized=True, s=10,c="#453781ff")
        subplot_ax.tick_params(axis="y", colors="#453781ff")
        ax2 = subplot_ax.twinx()
        ax2.scatter(frequency, -phase_shift, rasterized=True, s=10, c="#20a387ff")
        ax2.tick_params(axis="y", colors="#20a387ff")
        self.plot_identity(subplot_ax, xlabel=r"f $[Hz]$", ylabel=r"|Z| $[\Omega]$",
                        ax_sci_notation=ax_sci_notation,
                        scientific_limit=scientific_limit,
                        log_scale=log_scale)
        self.plot_identity(ax2, ylabel="\u03c6 [\u00b0]",
                        y_lim=[self.round_tenth(-phase_shift)[0],
                               self.round_tenth(-phase_shift)[1]],
                        log_scale=log_scale, step_size_y=10)

    def nyquist_fit(self, subplot_ax, frequency, real_impedance, imaginary_impedance,
                    fitted_impedance, chi, suggested_circuit, colorbar:bool=True,
                    ax_sci_notation = None, scientific_limit:int=3,
                    scientific_label_colorbar=False, legend_label=False,
                    voltage:float = None, color_map:str="viridis",
                    norm_color=None):
        """Defines the nyquist plot for fitted data

        Args:
            subplot_ax (ax): Subplot axis
            frequency (np.array): Frequency array.
            real_impedance (np.array): Real impedance array.
            imaginary_impedance (np.array): Imaginary impedance array.
            fitted_impedance (np.array): Fitted impedance array.
            chi (float): Chi value of the fit.
            suggested_circuit (str): The string definition of the suggested circuit.
            colorbar (bool, optional): If True, adds a colorbar. Defaults to True.
            ax_sci_notation (bool, optional): If True, adds scientific notation to the axis. Defaults to None.
            scientific_limit (int, optional): If ax_sci_notation is True, defines the number of significant digits. Defaults to None.
            scientific_label_colorbar (bool, optional): If True, adds scientific notation to the colorbar. Defaults to False.
            legend_label (bool, optional): If True, adds a legend. Defaults to False.
            voltage (float, optional): Voltage of the circuit. Defaults to None.
            color_map (str, optional): Color map. Defaults to "viridis".
            norm_color (bool, optional): If True, normalizes the colorbar. Defaults to None.
        """
        log.info("Creating a fitted Nyquist plot")
        nyquist_label = fr" v = {voltage} [V], \
                          $\chi_{{linKK}}^{2}$ = {np.format_float_scientific(chi, 3)}" \
                          if voltage else fr"$\chi^{2}$ = {np.format_float_scientific(chi, 3)}"

        norm = mcl.LogNorm(vmin=min(frequency), vmax=max(frequency)) if norm_color else None
        nyquist_plot = subplot_ax.scatter(real_impedance, -imaginary_impedance,
                                        c=frequency, norm=norm, s=10,
                                        cmap=color_map,rasterized=True,
                                        label=nyquist_label)

        subplot_ax.plot(np.real(fitted_impedance), -np.imag(fitted_impedance),
                        label=f"Fitted with {suggested_circuit}", color="k")

        self.plot_identity(subplot_ax, xlabel=r"Z' $[\Omega]$", ylabel=r"-Z'' $[\Omega]$",
                               x_lim=[0, max(real_impedance) +200],
                               y_lim=[0, max(-imaginary_impedance) +200],
                               ax_sci_notation=ax_sci_notation,
                               scientific_limit=scientific_limit)

        if legend_label:
            _, labels = subplot_ax.get_legend_handles_labels()
            new_handles= [Line2D([0], [0], marker='o',
                          markerfacecolor="black",
                          markeredgecolor="black", markersize=3, ls=''),
                          Line2D([0], [0],
                          color="black", markersize=3, lw=1)]
            subplot_ax.legend(new_handles, labels, loc="upper left", fontsize=5.5)

        if colorbar:
            self.add_colorbar(nyquist_plot, subplot_ax, scientific_label_colorbar,
                              scientific_limit=scientific_limit,
                              colorbar_label=r"f $[Hz]$")
        self.ax = subplot_ax

    def residual(self, subplot_ax, frequency, res_real, res_imag,
                log_scale='x', ax_sci_notation = None,
                scientific_limit:int=3):
        """Defines the residual plot for raw data

        Args:
            subplot_ax (ax): Subplot axis.
            frequency (np.array): Frequency array.
            res_real (np.array): Real residual array.
            res_imag (np.array): Imaginary residual array.
            log_scale (str, optional): If 'x', plots the x axis in log scale. Defaults to 'x'.
            ax_sci_notation (bool, optional): If True, adds scientific notation to the axis. Defaults to None.
            scientific_limit (int, optional): If ax_sci_notation is True, defines the number of significant digits. Defaults to None.
        """

        log.info("Creating a residual plot")
        subplot_ax.plot(frequency, res_real, label=r"$\Delta_{real}$", color="#453781ff",
                linestyle="--", marker='o')
        subplot_ax.plot(frequency, res_imag, label=r"$\Delta_{imaginary}$", color="#20a387ff",
                linestyle="--", marker='o')

        self.plot_identity(subplot_ax, xlabel=r"f $[Hz]$", ylabel=r"$\Delta$(residuals)",
                                ax_sci_notation=ax_sci_notation,
                                scientific_limit=scientific_limit, log_scale=log_scale)
        subplot_ax.legend(loc="lower right", fontsize=5.5)

    def compose_eis_subplot(self, plots:list):
        """Compose the EIS subplot

        Args:
            plots (list): List of plots to be composed.

        Returns:
            fig, ax: Figure and axis of the subplot.
        """

        plt.close('all')
        if len(plots)==1:
            fig = plt.figure(figsize=(3.5,3))
            spec = fig.add_gridspec(1, 1)
            ax = fig.add_subplot(spec[0,0])
            return fig, [ax]

        if len(plots) == 2:
            fig_size = 9 if ("nyquist" and "nyquist_fit") in plots else 8.5
            fig = plt.figure(figsize=(fig_size, 4))
            spec = fig.add_gridspec(1, 2)
            ax1 = fig.add_subplot(spec[0, 0])
            ax2= fig.add_subplot(spec[0, 1])
            return fig, [ax1, ax2]

        if len(plots) == 3:
            fig_size= 7 if ("nyquist" and "nyquist_fit" and "bode") in plots else 6.5
            fig = plt.figure(figsize=(fig_size, 5))
            spec = fig.add_gridspec(2, 2)
            if "residual" in plots:
                ax1 = fig.add_subplot(spec[0, 0])
                ax2 = fig.add_subplot(spec[0, 1])
                ax3 = fig.add_subplot(spec[1, :])
            else:
                ax1 = fig.add_subplot(spec[0, 0])
                ax2 = fig.add_subplot(spec[1, 0])
                ax3 = fig.add_subplot(spec[:, 1])
            return fig, [ax1, ax2, ax3]

        if len(plots) == 4:
            fig = plt.figure(figsize=(7.5, 6))
            spec = fig.add_gridspec(2, 2)
            ax1 = fig.add_subplot(spec[0, 0])
            ax2= fig.add_subplot(spec[0, 1])
            ax3 = fig.add_subplot(spec[1, 0])
            ax4 = fig.add_subplot(spec[1, 1])
            return fig, [ax1, ax2, ax3, ax4]

        if len(plots) == 0:
            log.error("No plots for EIS were selected.")
            return Exception(f"No plots for EIS were selected for plot {self.plot_type}.")

        log.error("Maximum plots for EIS is exceeded.")
        return Exception(f"Maximum plots for EIS is exceeded for plot {self.plot_type}.")
