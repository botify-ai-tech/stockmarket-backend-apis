from kiteconnect import KiteConnect
from datetime import datetime
from dateutil.tz import tzoffset
from talib import abstract
import numpy as np

import time
from functools import wraps

def timing_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()  # Record the start time
        result = func(*args, **kwargs)  # Call the wrapped function
        end_time = time.time()  # Record the end time
        elapsed_time = end_time - start_time  # Calculate elapsed time
        print(f"Function '{func.__name__}' executed in {elapsed_time:.4f} seconds")
        return result
    return wrapper

@timing_decorator
def setup_kite()->KiteConnect:
    kite = KiteConnect(api_key="vo2ciygkrkvlph31")
    return kite

@timing_decorator
def convert_data(data:list[dict]):
    timestamp = []
    close = []
    open = []
    high = []
    low = []

    for single_candle in data:
        timestamp.append(single_candle['date'])
        close.append(single_candle['close'])
        # high.append(single_candle['high'])
    
    close = np.array(close,dtype=np.float64)
    timestamp = np.array(timestamp,dtype=object)
    return close,timestamp

@timing_decorator
def find_start_index(timestamp:np.ndarray):
    target_dt = datetime(2024, 7, 15, 9, 15, tzinfo=tzoffset(None, 19800))
    # target_dt_naive = target_dt.replace(tzinfo=None) - timedelta(seconds=19800)
    # print(target_dt_naive)
    indices = np.where(timestamp == target_dt)[0]
    return indices[0]

@timing_decorator
def sma(data:np.ndarray,period:int):
    SMA = abstract.Function('sma')
    return SMA(data,period)

@timing_decorator
def detect_cross_over(sma_12,sma_26,start_index):
    for i in range(start_index,len(sma_12)):
        if (sma_12[i-1] < sma_26[i-1]) and (sma_12[i] > sma_26[i]):
            print(i)
            return i - 1

@timing_decorator
def calculate_target(close:float,target_percentage:float):
    return close * ( 1 + (target_percentage/100))

@timing_decorator
def calculate_stoploss(close:float,target_percentage:float):
    return close * ( 1 - (target_percentage/100))

@timing_decorator
def target_stoploss_checker(target:float,stop_loss:float,data:np.ndarray):
    for i in range(len(data)):
        if data[i] > target:
            print("TAREGT HIT")
            return i 
        elif data[i] < stop_loss:
            print("STOP LOSS HIT")
            return i 
    return -1


kite_connect = setup_kite()

access_token = 'P0Jy8EoLsy1hK5fe84JICt9udS3hQDYZ'

kite_connect.set_access_token(access_token)


target_percentage = 5
stoploss_percentage = 2


history_data = kite_connect.historical_data(instrument_token='128028676',from_date='2024-06-15',to_date='2024-08-13',interval='minute')

close, timestamp = convert_data(history_data)

day_start_index = find_start_index(timestamp=timestamp)
sma_12 = sma(close,period=12)
sma_26 = sma(close,period=26)
cross_over_index = detect_cross_over(sma_12,sma_26,day_start_index)

print(timestamp[cross_over_index],close[cross_over_index], "Entry"," ","Buy")
target = calculate_target(close[cross_over_index],target_percentage)
stoploss = calculate_stoploss(close[cross_over_index],stoploss_percentage)
# print(target,stoploss)

print(
    cross_over_index - day_start_index
)

one_day_dfference = cross_over_index - day_start_index
one_day_offset = day_start_index + one_day_dfference
day_end_index = cross_over_index + (375 - one_day_dfference)

# print(
#     timestamp[one_day_offset:day_end_index]
# )


tg_sl_index = target_stoploss_checker(target,stoploss,close[one_day_offset:day_end_index])

print(
    timestamp[day_end_index-15],close[day_end_index-15]
)

if tg_sl_index == -1:
    print(
        timestamp[day_end_index-15],close[day_end_index-15],"SELL"," ","Square off", close[day_end_index-15] - close[cross_over_index] 
    )




# print(len(sma_12),len(sma_26))
# offset = 375
# print(timestamp[start_index:(start_index + offset )])

