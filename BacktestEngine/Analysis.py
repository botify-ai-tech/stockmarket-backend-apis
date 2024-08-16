import numpy as np

def cross_over(sma_12: np.ndarray, sma_26: np.ndarray) -> int:
    cross_over = np.where((sma_12[:-1] < sma_26[:-1]) & (sma_12[1:] > sma_26[1:]))[0]
    return cross_over[0] if len(cross_over) > 0 else -1




