from pydantic import BaseModel

class Zerodh(BaseModel):
    stock_name:str
    from_date:str
    to_date:str
    interval:str
    target_percentage:float
    stoploss_percentage:float





