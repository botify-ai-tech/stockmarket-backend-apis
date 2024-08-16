import pandas as pd

instrument_list = pd.read_csv("https://api.kite.trade/instruments")

instrument_list.to_feather('instrument.feather')