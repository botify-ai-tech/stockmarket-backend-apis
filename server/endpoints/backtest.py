import time
from server.utils.BacktestEngine.data import process_historic_data
from server.utils.BacktestEngine.zerodha import setup_kite, fetch_data
from server.utils.BacktestEngine.data import process_user_input
from server.utils.BacktestEngine.operations import genreate_from_date
from server.utils.BacktestEngine.mis import mis_run
from server.utils.BacktestEngine.cnc import cnc_run,cnc_run_v2
from fastapi import APIRouter
from server.schemas.backtest import UserInput
from dotenv import load_dotenv
load_dotenv()

backtest_router = APIRouter()


@backtest_router.post("")
def run(backtest_parameter:UserInput):
    print("user_input->",backtest_parameter)
    kite = setup_kite()

    from_date = genreate_from_date(to_date=backtest_parameter.to_date)
    # strategy_start_date = 2024-07-15, from_date as 2024-06-15 For indicator
    user_input = process_user_input(
                            instrument=backtest_parameter.stock_name,
                            from_date=from_date,
                            to_date=backtest_parameter.to_date,
                            interval=backtest_parameter.interval,
                            target_percentage=backtest_parameter.target_percentage,
                            stoploss_percentage=backtest_parameter.stoploss_percentage
                        )
    historic_data = fetch_data(user_input=user_input,kite=kite)
    timestamp, close = process_historic_data(historic_data)
    execution_time_start = time.time()
    if backtest_parameter.mis:
        result = mis_run(
            timestamp=timestamp,
            close=close,
            strategy_start_date=backtest_parameter.from_date,
            user_input=user_input
        )
    else:
       result = cnc_run(
           close = close,
           timestamp=timestamp,
           strategy_start_date=backtest_parameter.from_date,
           user_input=user_input
       )
    print("TOTAL EXECUTION TIME:",time.time()-execution_time_start)

    return result

    
