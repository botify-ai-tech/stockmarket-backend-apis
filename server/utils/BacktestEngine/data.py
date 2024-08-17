import numpy as np
from .fileread import fetch_instrument_token
def process_user_input(instrument:str,from_date:str,to_date:str,interval:str,target_percentage:float,stoploss_percentage:float)->dict:
    return {
        'instrument': fetch_instrument_token(instrument=instrument),
        'from_date':from_date,
        'to_date':to_date,
        'interval':interval,
        'target':target_percentage,
        'stoploss':stoploss_percentage
    }


def process_historic_data(data:list[dict]):
    
    timestamp = np.array([data['date'] for data in data],dtype=object)
    close = np.array([data['close'] for data in data],dtype=np.float64)

    return timestamp, close
