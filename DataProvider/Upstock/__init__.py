from DataProvider.Upstock.main import Upstox


def run(instrument: str, interval: str, from_date: str, to_date: str) -> Upstox:
    try:
        upstox_object = Upstox(instrument=instrument, interval=interval, from_date=from_date, to_date=to_date)
        upstox_object.process()
    
    except Exception as e:
        raise RuntimeError(f"An error occurred: {e}")
    
    return upstox_object