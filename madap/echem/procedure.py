from abc import ABC, abstractmethod


class EChemProcedure(ABC):

    @abstractmethod
    def analyze(self):
        pass

    @abstractmethod
    def plot(self, save_dir:str, plots:list, optional_name:str):
        pass

    @abstractmethod
    def save_data(self, save_dir:str, optional_name:str):
        pass

    @abstractmethod
    def perform_all_actions(self, save_dir:str, plots:list, optional_name:str):
        pass