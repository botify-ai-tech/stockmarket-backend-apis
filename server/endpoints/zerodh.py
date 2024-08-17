
from dotenv import load_dotenv

from server.utils.BacktestEngine.data import process_historic_data
from server.utils.BacktestEngine.zerodha import setup_kite, fetch_data
from server.utils.BacktestEngine.data import process_user_input
from server.utils.BacktestEngine.indicator import sma
from server.utils.BacktestEngine.utils import find_start_index
from server.utils.BacktestEngine.analysis import cross_over
from server.utils.BacktestEngine.operations import target_stoploss_checker,calculate_target,calculate_stoploss,update_result_dict
from server.utils.BacktestEngine.const import Offset
from fastapi import APIRouter

backtest_router = APIRouter()


@backtest_router.post("/backtest")
def run():
    kite = setup_kite()

    # strategy_start_date = 2024-07-15, from_date as 2024-06-15 For indicator
    user_input = process_user_input(instrument='SBIN',from_date='2024-06-15',to_date='2024-08-13',interval='minute',target_percentage=5,stoploss_percentage=2)
    historic_data = fetch_data(user_input=user_input,kite=kite)
    timestamp, close = process_historic_data(historic_data)

    print('TARGET PERCENTAGE:',user_input['target'])
    print('STOPLOSS PERCENTAGE:',user_input['stoploss'])
    # for now assuming indicator = sma, period given is 12 and 26
    sma_12 = sma(data=close,period=12)
    sma_26 = sma(data=close,period=26)

    strategy_start_date = '2024-07-15'
    start_index = find_start_index(timestamp=timestamp,taregt_dt=strategy_start_date) # Find The index of element Which matches the start date with time as 09:15
    square_off_index = start_index + Offset.one_day_square_off
    day_end_index = start_index + Offset.one_day
    trades = []
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
    target_stoploss = False
    day_count = len(timestamp[start_index:]) // Offset.one_day
    no_of_day = 0
    result = {}
    while no_of_day != day_count:
    # while start_index + Offset.one_day < len(close):
        
        print("FIRST DATA OF THE DAY:",timestamp[start_index])
        cross_over_index_offset = cross_over(sma_12[start_index:day_end_index], sma_26[start_index:day_end_index])
        if cross_over_index_offset == -1:
            print("No Cross Over for the day")

            ###
            """
            NO ENTRY THE WHOLE DAY
            """
            start_index += Offset.one_day
            day_end_index += Offset.one_day
            square_off_index = square_off_index +Offset.one_day
            ###
            no_of_day += 1
            continue
        
        cross_over_index_offset += 1
        buy_index = start_index + cross_over_index_offset
        buy_price = close[buy_index]

        print(f"DATE AND TIME: {timestamp[buy_index]}, Price: {buy_price:.2f}, BUY/SELL: BUY, TRIGGER: ENTRY")
        trades.append({'Date':timestamp[buy_index],'price:':buy_price,'Buy/Sell':'BUY','Trigger':'ENTRY'})
        
        target = calculate_target(close=close[buy_index],target_percentage=user_input['target'])
        stoploss = calculate_stoploss(close=close[buy_index],stoploss_percentage=user_input['stoploss'])

        target_stoploss_index,target_stoploss_label = target_stoploss_checker(target=target,stop_loss=stoploss,data = close[start_index + cross_over_index_offset +1 : square_off_index ])
        
        if target_stoploss_index == -1:
            sell_index = square_off_index
            sell_price = close[square_off_index]
            print("DATE AND TIME:",timestamp[sell_index],"PRICE:",sell_price,"BUY/SELL:SELL","TRIGGER:SQUARE OFF")
            trades.append({'Date':timestamp[sell_index],'price:':sell_price,'Buy/Sell':'BUY','Trigger':'SQUARE OFF'})
            update_result_dict(stats,buy_price=buy_price,sell_price=sell_price)
            
            ###
            """
            IF ENTRY AND NO TAREGT OR STOPLOSS HIT
            """
            if target_stoploss:
                """
                    SECOND OR GREATER TRADE OF THE DAY
                """
                start_index = start_index + ((day_end_index - start_index))

            else:
                """
                    FIRST TRADE OF THE DAY
                """
                start_index = start_index + Offset.one_day 
            
            
            day_end_index = day_end_index + Offset.one_day
            square_off_index = square_off_index + Offset.one_day
            ####
            target_stoploss = False
            no_of_day += 1
        else:
            target_stoploss = True

            sell_index = start_index + target_stoploss_index
            sell_price = close[sell_index]
            print("DATE AND TIME:",timestamp[sell_index],"PRICE:",sell_price,"BUY/SELL:SELL","TRIGGER:",target_stoploss_label)
            trades.append({'Date':timestamp[sell_index],'price:':sell_price,'Buy/Sell':'BUY','Trigger':target_stoploss_label})
            update_result_dict(stats,buy_price=buy_price,sell_price=sell_price)
            # update_result_dict(stats)
            ###
            """
            IF TARGET/STOPLOSS HIT, THE ITERATION WILL CONTINUE FOR THE SAME DAY
            """
            start_index += target_stoploss_index + 1
            ###

        # if count == 20:
            # break
        # count += 1
    stats_result = {
        'Total Number of Trades':stats['trade_count'],
        'Winning Streak':stats['win_streak'],
        'Number of Wins':stats['win'],
        'Losing Streak':stats['loss_streak'],
        'Number of Losses':stats['loss'],
        'Max Loss':stats['max_loss'],
        'Max gains':stats['max_gain']

    }
    result={
        'Trades':trades,
        'stats':stats_result
    }
    return result

    
