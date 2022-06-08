from abc import ABC, abstractmethod


class EChemProcedure(ABC):
    
    @abstractmethod
    def analyse():
        pass
    
    @abstractmethod
    def plot():
        pass