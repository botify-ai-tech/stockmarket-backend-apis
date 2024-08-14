import numpy as np
from abc import ABC, abstractmethod
from DataProvider.Upstock.main import UpstoxProvider



class BacktestData(ABC):
    @abstractmethod
    def process(self):
        pass

class UpstockData(BacktestData):
    def process(self,
                timestamp:list,
                open:list,
                high:list,
                low:list,
                close:list,
                open_interests:list
            ) -> None:
        
        self.timestamp:np.ndarray = np.array(timestamp, dtype=object)
        self.open:np.ndarray = np.array(open, dtype=np.float64)
        self.close:np.ndarray = np.array(close ,dtype=np.float64)
        self.high:np.ndarray = np.array(high, dtype=np.float64)
        self.low:np.ndarray = np.array(low, dtype=np.int64)
        self.open_interests = np.array(open_interests, dtype=np.int64)

class BacktestParameters:
    def __init__(self,start_date:str,end_date:str,entry_condition:dict,exit_condition:dict,instrument:str,interval:str,stoploss_percentage:float,target_percentage:float)->None:
        self.start_date = start_date
        self.end_date = end_date
        self.entry_condition = entry_condition
        self.exit_condition = exit_condition
        self.instrument = instrument
        self.interval = interval
        self.target_percentage: float = None
        self.stoploss_percentage: float = None



class Backtest:

    def __init__(self,parameters:BacktestParameters,provider:str='upstock') -> None:
        self.provider = provider
        self.parameters = parameters
        

    def create_data_object(self) -> BacktestData:
        """Factory method to create a data object based on the provider."""
        if self.provider == "upstock":
            
            self.data_provider = UpstoxProvider(
                instrument=self.parameters.instrument,
                from_date=self.parameters.start_date,
                interval=self.parameters.interval
            )
            self.data_provider.process()
            self.data = UpstockData()
            self.data.process(
                timestamp = self.data_provider.timestamps,
                open = self.data_provider.opens,
                high = self.data_provider.highs,
                low = self.data_provider.lows,
                close = self.data_provider.closes,
                open_interests = self.data_provider.open_intrests
            )
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
    
    
    def entry_conidition(self):
        ...
    
    def exit_condition(self):
        ...
    
    
    
        


