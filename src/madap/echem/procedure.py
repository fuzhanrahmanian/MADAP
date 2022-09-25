"""This module defines the abstract class for the blueprint from all method's behaviours."""
from abc import ABC, abstractmethod


class EChemProcedure(ABC):
    """ Abstract class for the blueprint from all method's behaviours.

    Args:
        ABC (class): Abstract Base Class
    """
    @abstractmethod
    def analyze(self):
        """Abstract method for the analysis of the data.
        """

    @abstractmethod
    def plot(self, save_dir:str, plots:list, optional_name:str):
        """Abstract method for the plotting of the data.

        Args:
            save_dir (str): The directory where the plots are saved.
            plots (list): The plots that are saved.
            optional_name (str): The optional name of the plot.
        """

    @abstractmethod
    def save_data(self, save_dir:str, optional_name:str):
        """Abstract method for the saving of the data.

        Args:
            save_dir (str): The directory where the data is saved.
            optional_name (str): The optional name of the data.
        """

    @abstractmethod
    def perform_all_actions(self, save_dir:str, plots:list, optional_name:str):
        """Abstract method for the performing of all actions.

        Args:
            save_dir (str): The directory where the data is saved.
            plots (list): The plots that are saved.
            optional_name (str): The optional name of the data.
        """
