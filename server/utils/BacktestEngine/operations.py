import numpy as np
from datetime import datetime,timedelta

def target_stoploss_checker(target: float, stop_loss: float, data: np.ndarray):
    hit_index = np.argmax((data > target) | (data < stop_loss))
    if hit_index == 0 and not ((data[0] > target) or (data[0] < stop_loss)):
        return -1,""
    print("TARGET HIT" if data[hit_index] > target else "STOP LOSS HIT")
    return hit_index, "TARGET" if data[hit_index] > target else "STOPLOSS"



def calculate_target(close: float, target_percentage: float) -> float:
    return close * (1 + target_percentage / 100)

def calculate_stoploss(close: float, stoploss_percentage: float) -> float:
    return close * (1 - stoploss_percentage / 100)


def update_result_dict(result_dict:dict,sell_price:float,buy_price:float) -> None:
    result_dict['trade_count'] += 1
    if sell_price > buy_price:
            print("WIN", " GAIN:",sell_price-buy_price)
            result_dict['win'] += 1
            
            result_dict['current_gain'] = sell_price - buy_price
            # result_dict['current_gain'] = current_gain

            if result_dict['current_gain'] > result_dict['max_gain']:
                result_dict['max_gain'] = result_dict['current_gain']
            

            result_dict['current_win_streak'] += 1

            if result_dict['current_win_streak'] > result_dict['win_streak']:
                result_dict['win_streak'] = result_dict['current_win_streak']
            result_dict['current_loss_streak'] = 0
        
    else:
        print("WIN", " LOSSES:",sell_price-buy_price)
        result_dict['current_loss_streak'] += 1
        result_dict['current_loss'] = sell_price - buy_price
        
        if abs(result_dict['current_loss']) > abs(result_dict['max_loss']):
            result_dict['max_loss'] = result_dict['current_loss']
        
        if result_dict['current_loss_streak'] > result_dict['loss_streak']:
            result_dict['loss_streak'] = result_dict['current_loss_streak']
        result_dict['current_win_streak'] = 0
        result_dict['loss'] += 1


def genreate_from_date(to_date:str):
    input_date = datetime.strptime(to_date, "%Y-%m-%d")
    prior_date = input_date - timedelta(days=60)
    return prior_date.strftime("%Y-%m-%d")