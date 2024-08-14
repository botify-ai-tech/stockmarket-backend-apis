import requests
import numpy as np
from datetime import datetime
from typing import Dict, Any
from typing import Any, List
from utils.utils import timing_decorator

class UpstoxProvider:
    BASE_URL = 'https://api.upstox.com/v2/historical-candle'
    
    @timing_decorator
    def __init__(self, instrument: str, interval: str, from_date: str, to_date: str) -> None:
        self.instrument = instrument
        self.interval = interval
        self.from_date = from_date
        self.to_date = to_date
        self.url = self.construct_url()
        self.response: requests.Response = None
        self.candle_data: Any = None
        self.timestamps = None
        self.opens = None
        self.highs = None
        self.lows = None
        self.closes = None
        self.volumes = None
        self.open_intrests = None

    @timing_decorator
    def construct_url(self) -> str:
        return f"{UpstoxProvider.BASE_URL}/{self.instrument}/{self.interval}/{self.from_date}/{self.to_date}"
    
    @timing_decorator
    def fetch_data(self) -> None:
        headers = {'Accept': 'application/json'}
        try:
            self.response = requests.get(url=self.url, headers=headers)
            self.response.raise_for_status()
        except requests.RequestException as e:
            raise ConnectionError(f"Failed to fetch data: {e}")
    
    @timing_decorator
    def extract_data(self) -> None:
        if not self.response or self.response.status_code != 200:
            raise ValueError("Invalid response from server")
        
        try:
            response_json = self.response.json()
            self.candle_data = response_json['data']['candles'][::-1]
        except (ValueError, KeyError) as e:
            raise ValueError(f"Failed to extract data: {e}")
    
    @timing_decorator
    def transform_data(self) -> None:
        timestamps = []
        opens = []
        highs = []
        lows = []
        closes = []
        volumes = []
        open_interests = []
        for candle in self.candle_data:
            if len(candle) != 7:
                raise ValueError("Unexpected data format in candle_data")

            timestamp_str, open_str, high_str, low_str, close_str, volume_str, open_interest_str = candle
            try:
                # Convert timestamp string to a human-readable string format
                timestamp = datetime.fromisoformat(timestamp_str).strftime('%Y-%m-%d %H:%M:%S')
                
                # Convert other string values to appropriate data types
                open_val = float(open_str)
                high_val = float(high_str)
                low_val = float(low_str)
                close_val = float(close_str)
                volume_val = int(volume_str)
                open_interest_val = int(open_interest_str)

                # Append converted values to their respective lists
                timestamps.append(timestamp)
                opens.append(open_val)
                highs.append(high_val)
                lows.append(low_val)
                closes.append(close_val)
                volumes.append(volume_val)
                open_interests.append(open_interest_val)

            except ValueError as e:
                raise ValueError(f"Error converting data: {e}")
            
        # self.timestamps = np.array(timestamps, dtype=object)
        # self.opens = np.array(opens, dtype=np.float64)
        # self.highs = np.array(highs, dtype=np.float64)
        # self.lows = np.array(lows, dtype=np.float64)
        # self.closes = np.array(closes, dtype=np.float64)
        # self.volumes = np.array(volumes, dtype=np.int64)
        # self.open_interests = np.array(open_interests, dtype=np.int64)
    

    def process(self) -> np.ndarray:
        self.fetch_data()
        self.extract_data()
        self.transform_data()