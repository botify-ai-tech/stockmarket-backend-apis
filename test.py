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
def detect_cross_over(sma_12,sma_26):
    for i in range(1,len(sma_12)):
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
            print("TARGET HIT")
            return i,"TARGET" 
        elif data[i] < stop_loss:
            print("STOPLOSS HIT")
            return i, "STOPLOSS"
    return -1,""


kite_connect = setup_kite()
print(kite_connect)

access_token = 'oy2TfeIMRHlHAr7FSMgZ9mNtGH635sM7'

kite_connect.set_access_token(access_token)




history_data = kite_connect.historical_data(instrument_token='128028676',from_date='2024-06-15',to_date='2024-08-13',interval='minute')

close, timestamp = convert_data(history_data)




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

tg_sl = False

start_index = find_start_index(timestamp=timestamp) # The Following timestamp would be of start date, 09:15
square_off_index = start_index + square_off_offset
day_end_index = start_index + square_off_offset


trade_count = 0


win = 0
loss = 0 

win_streak = 0
loss_streak = 0
current_win_streak = 0
current_loss_streak = 0

current_gain = 0
current_loss = 0

max_gain = 0
max_loss = 0
while True:
    
    

    cross_over_index_offset = detect_cross_over(
            sma_12=sma_12[start_index:day_end_index],
            sma_26=sma_26[start_index:day_end_index]
        )
    
    

    # print("BUY ENTRY->",timestamp[start_index + cross_over_index_offset + 1], close[start_index + cross_over_index_offset])
    print("DATE AND TIME:",timestamp[start_index + cross_over_index_offset ]," Price:",close[start_index + cross_over_index_offset ],"BUY/SELL:BUY","TRIGGER:","ENTRY")
    buy_price = close[start_index + cross_over_index_offset ]
    if cross_over_index_offset == -1:
        print("No Cross Over for the day")
        
        start_index += one_day_offset
        day_end_index += one_day_offset
        square_off_index = square_off_index + one_day_offset
        
        continue
    
        
    
    target = calculate_target(close=close[start_index + cross_over_index_offset],target_percentage=target_percentage)
    stoploss = calculate_stoploss(close=close[start_index + cross_over_index_offset],stoploss_percentage=stoploss_percentage)
    tg_sl_index_offset,tg_sl_label = target_stoploss_checker(target,stoploss,close[start_index + cross_over_index_offset + 1 : square_off_index])
    

    
    
    
    if tg_sl_index_offset == -1:
        
        if tg_sl:
            start_index = start_index + ((day_end_index - start_index) + (one_day_offset - square_off_offset))
        else:
            start_index = start_index + one_day_offset

        # print("SQUARING OFF SELL",timestamp[square_off_index],close[square_off_index])
        print("DATE AND TIME:",timestamp[square_off_index],"PRICE:",close[start_index + cross_over_index_offset ],"BUY/SELL:SELL","TRIGGER:SQUARE OFF")
        sell_price = close[start_index + cross_over_index_offset ]
        
        if sell_price > buy_price:
            print("WIN", " GAIN:",sell_price-buy_price)
            win += 1
            
            current_gain = sell_price - buy_price
            if current_gain > max_gain:
                max_gain = current_gain
            
            current_win_streak += 1
            if current_win_streak > win_streak:
                win_streak = current_win_streak
            current_loss_streak = 0
        
        else:
            print("WIN", " LOSSES:",sell_price-buy_price)
            current_loss_streak += 1
            current_loss = sell_price - buy_price
            
            if abs(current_loss) > abs(max_loss):
                max_loss = current_loss
            if current_loss_streak > loss_streak:
                loss_streak = current_loss_streak
            current_win_streak = 0
            loss += 1
        
        trade_count += 1
        day_end_index = day_end_index + one_day_offset
        square_off_index = square_off_index + one_day_offset
    
    else:
        tg_sl = True
        trade_count += 1
        # print("TG/SL SELL->",timestamp[start_index + tg_sl_index_offset])
        print("DATE AND TIME:",timestamp[start_index + tg_sl_index_offset],"PRICE:",close[start_index + tg_sl_index_offset],"BUY/SELL:SELL","TRIGGER:",tg_sl_label)
        sell_price = close[start_index + tg_sl_index_offset]
        
        if sell_price > buy_price:
            print("WIN", " GAIN:",sell_price-buy_price)
            win += 1
            
            current_gain = sell_price - buy_price
            if current_gain > max_gain:
                max_gain = current_gain
            
            current_win_streak += 1
            if current_win_streak > win_streak:
                win_streak = current_win_streak
            current_loss_streak = 0
        
        else:
            print("WIN", " LOSSES:",sell_price-buy_price)
            current_loss_streak += 1
            current_loss = sell_price - buy_price
            
            if abs(current_loss) > abs(max_loss):
                max_loss = current_loss
            if current_loss_streak > loss_streak:
                loss_streak = current_loss_streak
            current_win_streak = 0
            loss += 1
        
        start_index = start_index + tg_sl_index_offset + 1  


       
    if count == 23:
        break
    count += 1

print("Trade Count=",trade_count)
print("Win->",win)
print("Loss->",loss)

print("win streak->",win_streak)
print("loss streak->",loss_streak)

print("Max Gains:",max_gain)
print("Max Losses:",max_loss)
