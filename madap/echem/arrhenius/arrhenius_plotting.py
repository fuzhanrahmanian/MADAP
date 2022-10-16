"""This module handles the plotting of the Arrhenius procedure"""
from matplotlib import pyplot as plt

from madap.logger import logger
from madap.plotting.plotting import Plots


log = logger.get_logger("arrhenius_plotting")

class ArrheniusPlotting(Plots):
    """General Plotting class for Arrhenius method.

    Args:
        Plots (class): Parent class for plotting all methods.
    """
    def __init__(self) -> None:
        super().__init__()
        self.plot_type = "Arrhenius"

    def arrhenius(self, subplot_ax, temperatures, log_conductivity, inverted_scale_temperatures,
            ax_sci_notation = None, scientific_limit: int = 3):
        """Defines the Arrhenius plot for raw data

        Args:
            subplot_ax (ax): Subplot axis
            temperatures (np.array): Array of temperatures
            log_conductivity (np.array): Array of log conductivity in [S/cm]
            inverted_scale_temperatures (np.array): Array of inverted scale temperatures in [1000/K]
            ax_sci_notation (bool, optional): If True, adds scientific notation to the axis. Defaults to None.
            scientific_limit (int, optional): If ax_sci_notation is True, defines the number of significant digits. Defaults to None.
        """

        log.info("Creating Arrhenius plot")
        subplot_ax2=subplot_ax.twiny()
        self.plot_identity(subplot_ax, xlabel=r"$\frac{1000}{T}$ $[K^{-1}]$",
                           ylabel=r"$\ln$($\sigma$) [$ln(S.cm^{-1})$]",
                           ax_sci_notation=ax_sci_notation,
                           scientific_limit=scientific_limit)

        subplot_ax2.scatter(temperatures, log_conductivity, s=10, c="#20a387ff", rasterized=True)
        self.plot_identity(subplot_ax2, xlabel="$T$ [\u00b0C]")
        self.set_xtick_for_two_axes(subplot_ax, subplot_ax2, [f"{ct:.1f}" for ct in inverted_scale_temperatures], temperatures, invert_axes=True)

    def arrhenius_fit(self, subplot_ax, temperatures, log_conductivity, inverted_scale_temperatures,
                    ln_conductivity_fit, activation, arrhenius_constant, r2_score,
                    ax_sci_notation = None, scientific_limit: int=3):
        """
        Defines the Arrhenius plot for fitted data

        Args:
            subplot_ax (ax): Subplot axis
            temperatures (np.array): Array of temperatures
            log_conductivity (np.array): Array of log conductivity in [S/cm]
            inverted_scale_temperatures (np.array): Array of inverted scale temperatures in [1000/K]
            ln_conductivity_fit (np.array): Array of fitted log conductivity in [S/cm]
            activation (float): Activation energy in [mJ/mol]
            arrhenius_constant (float): Arrhenius constant in [mJ/mol]
            r2_score (float): R2 score of the fit
            ax_sci_notation (bool, optional): Weather or not scientific notation should be adopted for axis. Defaults to None.
            scientific_limit (int, optional): Number of significant digits. Defaults to 3.
        """
        log.info("Creating a fitted Arrhenius plot")
        subplot_ax2=subplot_ax.twiny()
        subplot_ax.plot(inverted_scale_temperatures, ln_conductivity_fit, c="#453781ff", linewidth=1, linestyle="--",
                        label=f" E  = {activation:.2f} [mJ.mol⁻¹] \n A  = {arrhenius_constant:.2f} [S.cm⁻¹] \n R² = {r2_score:.2f}")

        subplot_ax2.scatter(temperatures, log_conductivity, s=10, c="#20a387ff", rasterized=True)
        subplot_ax2.invert_xaxis()
        self.plot_identity(subplot_ax, xlabel=r"$\frac{1000}{T}$ $[K^{-1}]$",
                           ylabel=r"$\ln$($\sigma$) [$ln(S.cm^{-1})$]",
                           ax_sci_notation=ax_sci_notation,
                           scientific_limit=scientific_limit)
        subplot_ax.legend(loc="upper right", fontsize=5.5)

        self.plot_identity(subplot_ax2, xlabel="$T$ [\u00b0C]")

    def compose_arrhenius_subplot(self, plots:list):
        """Creates subplots template for the Arrhenius plots.

        Args:
            plots (list): List of plots to be composed.

        Returns:
            fig, ax: Figure and axis of the subplot.
        """
        plt.close('all')
        if len(plots)==1:
            fig = plt.figure(figsize=(3, 3))
            spec = fig.add_gridspec(1, 1)
            ax = fig.add_subplot(spec[0,0])
            return fig, [ax]

        if len(plots) == 2:
            fig = plt.figure(figsize=(6, 3))
            spec = fig.add_gridspec(1, 2)
            ax1 = fig.add_subplot(spec[0, 0])
            ax2 = fig.add_subplot(spec[0, 1])
            return fig, [ax1, ax2]

        return Exception(f"Number of plots not supported for plot type {self.plot_type}")
