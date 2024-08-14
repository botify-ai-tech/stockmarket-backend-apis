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

#@timing_decorator
def setup_kite()->KiteConnect:
    kite = KiteConnect(api_key="vo2ciygkrkvlph31")
    return kite

#@timing_decorator
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

#@timing_decorator
def find_start_index(timestamp:np.ndarray):
    target_dt = datetime(2024, 7, 15, 9, 15, tzinfo=tzoffset(None, 19800))
    # target_dt_naive = target_dt.replace(tzinfo=None) - timedelta(seconds=19800)
    # print(target_dt_naive)
    indices = np.where(timestamp == target_dt)[0]
    return indices[0]

#@timing_decorator
def sma(data:np.ndarray,period:int):
    SMA = abstract.Function('sma')
    return SMA(data,period)

#@timing_decorator
def detect_cross_over(sma_12,sma_26,start_index,end_index):
    for i in range(start_index,len(sma_12)):
        if (sma_12[i-1] < sma_26[i-1]) and (sma_12[i] > sma_26[i]):
            return i - 1
    return -1

#@timing_decorator
def calculate_target(close:float,target_percentage:float):
    return close * ( 1 + (target_percentage/100))

#@timing_decorator
def calculate_stoploss(close:float,stoploss_percentage:float):
    return close * ( 1 - (stoploss_percentage/100))

#   @timing_decorator
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




history_data = kite_connect.historical_data(instrument_token='128028676',from_date='2024-06-15',to_date='2024-08-13',interval='minute')

close, timestamp = convert_data(history_data)

# day_start_index = find_start_index(timestamp=timestamp)



# cross_over_index = detect_cross_over(sma_12,sma_26,day_start_index)

# print(timestamp[cross_over_index],close[cross_over_index], "Entry"," ","Buy")
# target = calculate_target(close[cross_over_index],target_percentage)
# stoploss = calculate_stoploss(close[cross_over_index],stoploss_percentage)
# print(target,stoploss)




# one_day_dfference = cross_over_index - day_start_index
# one_day_offset = day_start_index + one_day_dfference
# square_off_index = cross_over_index + (360 - one_day_dfference)





# print(timestamp[one_day_offset:square_off_index])

# tg_sl_index = target_stoploss_checker(target,stoploss,close[one_day_offset:square_off_index])



# if tg_sl_index == -1:
#     print(
#         timestamp[square_off_index],close[square_off_index],"SELL"," ","Square off", close[square_off_index] - close[cross_over_index] 
#     )


# consdering 1minute candle
square_off_offset = 360 # 15:15
one_day_offset = 375 #15:29

# Parameters
target_percentage = 5
stoploss_percentage = 2


# Indicator calculation
sma_12 = sma(close,period=12)
sma_26 = sma(close,period=26)
count = 0 

day_start_index = find_start_index(timestamp=timestamp) # The Following timestamp would be of start date, 09:15
while True:
    
    print("FIRST DATA->",timestamp[day_start_index])

    square_off_index = day_start_index + square_off_offset
    
    cross_over_index = detect_cross_over(
            sma_12=sma_12,
            sma_26=sma_26,
            start_index=day_start_index,
            end_index = (day_start_index + square_off_offset)
        )
    

    print("CROSSOVER->",timestamp[cross_over_index], close[cross_over_index+1])
    if cross_over_index == -1:
        print("No Cross Over for the day")
        #Change the current_day_index for the next day index
        continue
    
    
    
    target = calculate_target(close=close[cross_over_index],target_percentage=target_percentage)
    stoploss = calculate_stoploss(close=close[cross_over_index],stoploss_percentage=stoploss_percentage)
    tg_sl_index = target_stoploss_checker(target,stoploss,close[cross_over_index + 1 : square_off_index])

    
    
    
    if tg_sl_index == -1:
        print(
            "Square off", timestamp[square_off_index]," ",close[square_off_index]
        )
    
    
    day_start_index += one_day_offset 

    
    

    # if cross_over_index == -1:
        # print("No cross over The whole day")
    if count == 2:
        break
    count += 1



# print(len(sma_12),len(sma_26))
# offset = 375
# print(timestamp[start_index:(start_index + offset )])

