from enum import Enum
from typing import Optional

from pydantic import BaseModel


class RatioBase(BaseModel):
    id: str = None
    nifty_sahre: str = None
    financial_ratio_analysis: list = None
    key_highlights: list = None
    stock_value: dict = None
    conclusion: dict = None

class CreateRatio(RatioBase):
    pass

class UpdateRatio(RatioBase):
    pass

class Symbol(BaseModel):
    company_name: str
