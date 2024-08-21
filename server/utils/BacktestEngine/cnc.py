import numpy as np
from server.utils.BacktestEngine.const import Offset
from server.utils.BacktestEngine.indicator import sma
from server.utils.BacktestEngine.utils import find_start_index
from server.utils.BacktestEngine.analysis import cross_over
from server.utils.BacktestEngine.operations import target_stoploss_checker,calculate_target,calculate_stoploss,update_result_dict

def cnc_run(
    close:np.ndarray,
    timestamp:np.ndarray,
    strategy_start_date:str,
    user_input:dict
):
    
    stats = {
        'trade_count':0,
        'current_gain':0,
        'current_loss':0,
        'max_gain':0,
        'max_loss':0,
        'current_gain':0,
        'current_loss':0,
        'max_gain':0,
        'max_loss':0,
        'win':0,
        'loss':0,
        'loss_streak':0,
        'win_streak':0,
        'current_win_streak':0,
        'current_loss_streak':0
    }

    # strategy_start_date = backtest_parameter.from_date
    start_index = find_start_index(timestamp=timestamp,taregt_dt=strategy_start_date) # Find The index of element Which matches the start date with time as 09:15
    # square_off_index = start_index + Offset.one_day_square_off
    day_end_index = start_index+ Offset.one_day_square_off

    sma_12 = sma(data=close,period=12)
    sma_26 = sma(data=close,period=26)

    day_count = len(timestamp[start_index:]) // Offset.one_day
    no_of_day = 0
    result = {}
    trades = []
    in_trade = False
    target_stoploss_index = -1

    same_day_trade = False
    
    while no_of_day != day_count:
        print("FIRST DATA OF THE DAY:",timestamp[start_index ])
        cross_over_index_offset = cross_over(sma_12[start_index:day_end_index+1], sma_26[start_index:day_end_index+1])
        
        if not in_trade:
            if cross_over_index_offset == -1:
                print("No cross overs for the day")
                start_index = start_index + Offset.one_day
                day_end_index += Offset.one_day
                no_of_day += 1
            else:
                cross_over_index_offset += 1
                buy_index = start_index + cross_over_index_offset
                buy_price = close[buy_index]
                target = calculate_target(close=close[buy_index],target_percentage=user_input['target'])
                stoploss = calculate_stoploss(close=close[buy_index],stoploss_percentage=user_input['stoploss'])
                trades.append({'Date':timestamp[buy_index],'price:':buy_price,'Buy/Sell':'BUY','Trigger':'ENTRY'})
                print('Date',timestamp[buy_index],'price:',buy_price,'Buy/Sell','BUY','Trigger','ENTRY')
                in_trade = True
                

        if in_trade:
            target_stoploss_index,target_stoploss_label = target_stoploss_checker(target=target,stop_loss=stoploss,data = close[start_index + cross_over_index_offset  : day_end_index +1 ])
            if target_stoploss_index == -1:
                print("NO TG/SL HIT FOR THE DAY.....",same_day_trade)
                if not same_day_trade:
                    start_index = start_index + Offset.one_day
                else:
                    print("CURRNET START INDEX:",timestamp[start_index])
                    start_index = (start_index - same_day_target_stoploss_index ) + (Offset.one_day) - 1
                    same_day_trade = False
                day_end_index = day_end_index + Offset.one_day
                no_of_day += 1
            else:
                sell_index = start_index + target_stoploss_index
                sell_price = close[sell_index]
                print('Date',timestamp[sell_index],'price:',sell_price,'Buy/Sell','BUY','Trigger',target_stoploss_label)
                start_index = start_index + target_stoploss_index + 1
                in_trade = False
                same_day_trade = True
                same_day_target_stoploss_index = target_stoploss_index 
        
        
    

def cnc_run_v2(
    close:np.ndarray,
    timestamp:np.ndarray,
    strategy_start_date:str,
    user_input:dict
):
    
    stats = {
        'trade_count':0,
        'current_gain':0,
        'current_loss':0,
        'max_gain':0,
        'max_loss':0,
        'current_gain':0,
        'current_loss':0,
        'max_gain':0,
        'max_loss':0,
        'win':0,
        'loss':0,
        'loss_streak':0,
        'win_streak':0,
        'current_win_streak':0,
        'current_loss_streak':0
    }

    # strategy_start_date = backtest_parameter.from_date
    start_index = find_start_index(timestamp=timestamp,taregt_dt=strategy_start_date) # Find The index of element Which matches the start date with time as 09:15
    # square_off_index = start_index + Offset.one_day_square_off
    day_end_index = start_index+ Offset.one_day_square_off

    sma_12 = sma(data=close,period=12)
    sma_26 = sma(data=close,period=26)

    day_count = len(timestamp[start_index:]) // Offset.one_day
    no_of_day = 0
    result = {}
    trades = []
    in_trade = False
    same_day_trade = False
    cross_over_index_offset = 0
    target_stoploss_index = 0
    count = 0
    while ((cross_over_index_offset != -1)  or (target_stoploss_index != -1)):
        print("FIRST DATA OF THE DAY:",timestamp[start_index])
        cross_over_index_offset = cross_over(sma_12[start_index:], sma_26[start_index:])
        
        buy_index = start_index +  cross_over_index_offset + 1
        buy_price = close[buy_index]
        target = calculate_target(close=close[buy_index],target_percentage=user_input['target'])
        stoploss = calculate_stoploss(close=close[buy_index],stoploss_percentage=user_input['stoploss'])
        trades.append({'Date':timestamp[buy_index],'price:':buy_price,'Buy/Sell':'BUY','Trigger':'ENTRY'})
        print('Date',timestamp[buy_index],'price:',buy_price,'Buy/Sell','BUY','Trigger','ENTRY')
        in_trade = True
        print(
            timestamp[buy_index + 1]
        )
        if in_trade:
            target_stoploss_index,target_stoploss_label = target_stoploss_checker(target=target,stop_loss=stoploss,data = close[buy_index + 1 : ])
            sell_index = start_index + (target_stoploss_index + 1)
            sell_price = close[sell_index]
            print('Date',timestamp[sell_index],'price:',sell_price,'Buy/Sell','BUY','Trigger',target_stoploss_label)
            start_index = start_index + target_stoploss_index + 2
        
        count += 1
        if count == 3:
            break
