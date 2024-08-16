import requests
import pandas as pd
from datetime import datetime

response = requests.get(
    'https://api.upstox.com/v2/market/holidays'
)

print(response.status_code)

# print(response.text)

holiday_list = response.json()['data']

year = '2024'

holiday_data = []
for day in holiday_list:
    single_holiday_data = {}
    if 'NSE' in day['closed_exchanges']:
        date_obj = datetime.strptime(day['date'], '%Y-%m-%d')
        single_holiday_data['date'] = date_obj
        single_holiday_data['description'] = day['description']
        holiday_data.append(single_holiday_data)  

df = pd.DataFrame(
    data=holiday_data,
    columns=['date', 'description']
)

df.to_feather('./Holidays/2024.feather')
