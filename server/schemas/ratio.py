from enum import Enum
from typing import Optional

from pydantic import BaseModel


class RatioBase(BaseModel):
    id: str = None
    nifty_sahre: str = None
    stock_name: str = None
    favourable_indicators: list= None
    unfavourable_indicators: list= None
    summary: str = None
    pros: list[str] = None
    cons: list[str] = None
    investment_recommendation: dict = None

class CreateRatio(RatioBase):
    pass

class UpdateRatio(RatioBase):
    pass

class Symbol(BaseModel):
    company_name: str
