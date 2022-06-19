from abc import ABC, abstractmethod


class EChemProcedure(ABC):

    @abstractmethod
    def analyze():
        pass

    @abstractmethod
    def plot():
        pass

    @abstractmethod
    def save_data():
        pass

    @abstractmethod
    def perform_all_actions():
        pass