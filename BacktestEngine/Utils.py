import numpy as np
from datetime import datetime
from dateutil.tz import tzoffset

def find_start_index(timestamp:np.ndarray,taregt_dt:str):

    date_object = datetime.strptime(taregt_dt,'%Y-%m-%d')
    target_dt = datetime(date_object.year, date_object.month, date_object.day, 9, 15, tzinfo=tzoffset(None, 19800))
    # indices = np.where(timestamp == target_dt)[0]
    index = np.searchsorted(timestamp, target_dt)
    return index if timestamp[index] == target_dt else -1