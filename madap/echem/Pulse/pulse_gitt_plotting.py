from matplotlib import pyplot as plt

from madap.logger import logger
from madap.plotting.plotting import Plots


log = logger.get_logger("gitt_plotting")

class ArrheniusPlotting(Plots):
    """General Plotting class for Pulse method.

    Args:
        Plots (class): Parent class for plotting all methods.
    """
    def __init__(self) -> None:
        super().__init__()
        self.plot_type = "GITT"

    


    def compose_gitt_subplot(self, plots:list):
        """Compose the EIS subplot

        Args:
            plots (list): List of plots to be composed.

        Returns:
            fig, ax: Figure and axis of the subplot.
        """