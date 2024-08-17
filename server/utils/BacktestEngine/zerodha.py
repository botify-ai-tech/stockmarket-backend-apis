import os
from kiteconnect import KiteConnect

def setup_kite()->None:
    
    kite = KiteConnect(api_key=os.getenv('API_KEY'))
    kite.set_access_token(access_token=os.getenv('ACCESS_TOKEN'))
    return kite

def fetch_data(user_input:dict, kite:KiteConnect)->list:
    return kite.historical_data(
        instrument_token = user_input['instrument'],
        from_date =  user_input['from_date'],
        to_date=user_input['to_date'],
        interval=user_input['interval']
    )