from pydantic import BaseModel

class UserInput(BaseModel):
    stock_name:str
    from_date:str
    to_date:str
    interval:str
    target_percentage:float
    stoploss_percentage:float
    mis:bool




