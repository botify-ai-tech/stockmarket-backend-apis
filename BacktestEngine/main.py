import datetime
from kiteconnect import KiteConnect
import os

user_input:dict = {
    "from_date":None,
    "to_date":None,
    "instrument":None,
    "interval":None
}


def setup_kite()->KiteConnect:
    global kite 
    kite = KiteConnect(api_key=os.getenv('APIAPI_KEY'))
    kite.





def fetch_data(
        from_date:str,
        to_date:str,
        instrument:str,
        interument:str
    ):
    ...