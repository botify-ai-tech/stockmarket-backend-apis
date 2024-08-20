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

    target_stoploss = False
    day_count = len(timestamp[start_index:]) // Offset.one_day
    no_of_day = 0
    result = {}
    trades = []
    
    in_trade = False
    # day_change = False
    target_stoploss_index = -1
    count = 0
    while no_of_day != day_count:
        # while start_index + Offset.one_day < len(close):

        print("FIRST DATA OF THE DAY:",timestamp[start_index])
        if not in_trade:
            # if target_stoploss_index != -1:
            #     print("TARGET STOP LOSS INDEX IS NOT -1")
            #     start_index += (Offset.one_day - (target_stoploss_index-1))
            #     target_stoploss_index = -1
            
            cross_over_index_offset = cross_over(sma_12[start_index:day_end_index], sma_26[start_index:day_end_index])
            
            if cross_over_index_offset == -1:
                print("No Cross Over for the day")
                ###
                """
                NO ENTRY THE WHOLE DAY
                """
                if target_stoploss_index == -1:
                    start_index += Offset.one_day
                else:
                    start_index += (Offset.one_day-target_stoploss_index)
                day_end_index += Offset.one_day
                no_of_day += 1
                ###
                continue

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
            target_stoploss_index,target_stoploss_label = target_stoploss_checker(target=target,stop_loss=stoploss,data = close[start_index + cross_over_index_offset + 1 : day_end_index ])
            if target_stoploss_index == -1:
                #   print("No Target or StopLoss Hit for the day")
                ###
                start_index = start_index + (Offset.one_day - start_index) + 1
                day_end_index += Offset.one_day
                cross_over_index_offset = -1 
                no_of_day += 1
                ###
                continue
            else:
                print("TG/SL INDEX",target_stoploss_index)
                sell_index = start_index + target_stoploss_index
                sell_price = close[sell_index]
                trades.append({'Date':timestamp[sell_index],'price:':sell_price,'Buy/Sell':'BUY','Trigger':target_stoploss_label})
                print('Date',timestamp[sell_index],'price:',sell_price,'Buy/Sell','BUY','Trigger',target_stoploss_label)
                start_index += target_stoploss_index + 1
                update_result_dict(stats,buy_price=buy_price,sell_price=sell_price)
                in_trade = False
        
        count += 1
        if count == 3:
            break

    
    # stats_result = {
        # 'Total Number of Trades':stats['trade_count'],
        # 'Winning Streak':stats['win_streak'],
        # 'Number of Wins':stats['win'],
        # 'Losing Streak':stats['loss_streak'],
        # 'Number of Losses':stats['loss'],
        # 'Max Loss':stats['max_loss'],
        # 'Max gains':stats['max_gain']
    # }
    # 
    # result={
        # 'Trades':trades,
        # 'stats':stats_result
    # }

    # return result

