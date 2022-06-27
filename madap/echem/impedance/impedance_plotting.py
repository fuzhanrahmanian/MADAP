from madap import logger
from matplotlib import pyplot as plt
from matplotlib.lines import Line2D
import matplotlib.colors as mcl
import numpy as np
from plotting import Plots


log = logger.get_logger("impedance_plotting")

class ImpedancePlotting(Plots):

    def nyquist(self, subplot_ax, frequency, real_impedance, imaginary_impedance,
                colorbar:bool=True, ax_sci_notation = None, scientific_limit=None,
                scientific_label_colorbar=False, legend_label=False,voltage:float = None,
                color_map:str="viridis", norm_color=None):
        # TODO docstring is not right fixation is needed
        """Sets up a Nyquist plots

        Args:
            ax (AxesSubplot): The ax of the subplot
            frequency (pandas.core.series.Series): The series with the frequency
            real_impedance (pandas.core.series.Series): The Series with Real Impedance
            imaginary_impedance (pandas.core.series.Series): The series with the imaginary impedance
            colorbar (bool, optional): Whether or not a colorbar is desired. Defaults to True.
            ax_sci_notation (str, optiopnal): whether or not an axis should be written with
                scientific notation. It can be 'x', 'y', 'both' or None.
            scientific_label (optional): Scientific notation will be used for numbers
                outside the range.Defaults to None.
            legend_label (str, optional): Label of the legend. Defaults to None.
            voltage (float, optional): whether or not the applied voltage should be added to legend.
            color_map (str, optional): Colormap to be used . Defaults to "viridis".
        """

        log.info("Creating Nyquist plot")
        norm = mcl.LogNorm(vmin=min(frequency), vmax=max(frequency)) if norm_color else None

        nyquist_plot = subplot_ax.scatter(real_impedance, -imaginary_impedance,
                                          c=frequency, norm=norm, s=10,
                                          cmap=color_map, rasterized=True,
                                          label=f"v = {voltage}[V]")

        nyquist_plot.set_clim(min(frequency), max(frequency))

        self.plot_identity(subplot_ax, xlabel=r"Z' $[\Omega]$", ylabel=r"-Z'' $[\Omega]$",
                            x_lim=[0, max(real_impedance)+200],
                            y_lim=[0, max(-imaginary_impedance)+200],
                            ax_sci_notation=ax_sci_notation,
                            scientific_limit=scientific_limit)

        if (legend_label and voltage != None):
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

        log.info("Creating a fitted Nyquist plot")
        nyquist_label = fr" v = {voltage}[V], $\chi$ = {np.format_float_scientific(chi, 3)}" if voltage else fr"$\chi$ = {np.format_float_scientific(chi, 3)}"

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

    def residual(self, subplot_ax, frequency, res_real, res_imag,
                log_scale='x', ax_sci_notation = None,
                scientific_limit:int=3):

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

        if len(plots)==1:
            fig = plt.figure(figsize=(3.5,3))
            spec = fig.add_gridspec(1, 1)
            ax = fig.add_subplot(spec[0,0])
            return fig, [ax]

        elif len(plots) == 2:
            fig_size = 9 if ("nyquist" and "nyquist_fit") in plots else 8.5
            fig = plt.figure(figsize=(fig_size, 4))
            spec = fig.add_gridspec(1, 2)
            ax1 = fig.add_subplot(spec[0, 0])
            ax2= fig.add_subplot(spec[0, 1])
            return fig, [ax1, ax2]

        elif len(plots) == 3:
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

        elif len(plots) == 4:
            fig = plt.figure(figsize=(7.5, 6))
            spec = fig.add_gridspec(2, 2)
            ax1 = fig.add_subplot(spec[0, 0])
            ax2= fig.add_subplot(spec[0, 1])
            ax3 = fig.add_subplot(spec[1, 0])
            ax4 = fig.add_subplot(spec[1, 1])
            return fig, [ax1, ax2, ax3, ax4]

        else:
            log.error("Maximum plots for EIS is exceeded.")
