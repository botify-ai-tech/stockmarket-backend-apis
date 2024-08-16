import os
import pandas as pd


def fetch_instrument_token(instrument:str)->str:
    instrument_file = pd.read_feather(
        f"{os.getenv('INSTRUMENT_FILE_PATH')}"
    )
    instrument_token = instrument_file[(instrument_file['tradingsymbol'] == instrument) & (instrument_file['instrument_type'] == 'EQ') & (instrument_file['exchange'] == 'NSE')]    
    return str(instrument_token.values[0][0])