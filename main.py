from DataProvider import Upstock

import time
from TechnicalIndicator import main

data_fetching_start = time.time()

data = Upstock.run(
    instrument='NSE_EQ%7CINE848E01016',
    interval='1minute',
    from_date='2024-08-09',
    to_date='2023-08-09'
)

print("ELT Time:",time.time()-data_fetching_start)

start_time = time.time()

main(
    high = data.highs,
    low = data.lows,
    close= data.closes
)

end_time = time.time() - start_time

print(end_time)