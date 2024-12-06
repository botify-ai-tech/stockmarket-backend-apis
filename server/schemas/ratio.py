from datetime import datetime
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

class CompanyBase(BaseModel):
    id:str = None
    share_name:str = None
    current_date:str = None
    share_symbol:str = None
    share_price:str = None
    market_cap:str = None
    high_low:str = None
    pe_ratio:str = None
    enterprise_value:str = None
    book_value:str = None
    dividend_yield:str = None
    promoter_holding:str = None
    eps:str = None
    sales_growth:str = None
    profit_growth:str = None
    roce:str = None
    cash:str = None
    debt:str = None
    roe:str = None
    face_value:str = None
    bse:str = None
    nse:str = None
    chart:list | dict = None
    s_pros:str = None
    s_cons:str = None
    s_peer_comparison:list | dict = None
    s_quarterly_results:list | dict = None
    s_profit_loss:list | dict = None
    s_balance_sheet:list | dict = None
    s_cash_flows:list | dict = None
    s_ratios:list | dict = None
    s_shareholding_pattern_quarterly:list | dict = None
    s_shareholding_pattern_yearly:list | dict = None
    s_documents:list | dict = None
    t_strengths:str = None
    t_limitations:str = None
    t_quarterly_results:list | dict = None
    t_profit_loss:list | dict = None
    t_balance_sheet_equity_and_liabilities:list | dict = None
    t_balance_sheet_assets:list | dict = None
    t_cash_flows:list | dict = None
    created_at:datetime = None
    updated_at:datetime = None