from talib import abstract
import numpy as np

def sma(data:np.ndarray,period:int):
    SMA = abstract.Function('sma')
    return SMA(data,period)