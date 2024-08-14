import talib
from talib import abstract
import numpy as np
from typing import Any
    

class Sma:
    def __init__(
            self,
            period:int,
            data:np.ndarray
    )->None:
        self.period:int = period
        self.SMA:Any =  abstract.Function('sma')
        self.data:np.ndarray = data
        # self.result = 
        

    def calculate(self):
        return self.SMA(
            self.data,
            timeperiod = self.period
        )