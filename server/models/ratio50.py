import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, Column, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship

from server.db.base_class import Base



class Company50(Base):
    id = Column(String, default=lambda: str(uuid.uuid4()), primary_key=True)
    share_name = Column(String)
    current_date = Column(String)
    share_symbol = Column(String)
    share_price = Column(String)
    compnay_info_doc = Column(String)
    share_price_percentage = Column(String)
    industry_pe = Column(String)
    sectore_pe = Column(String)
    market_cap = Column(String)
    high_low = Column(String)
    pe_ratio = Column(String)
    pb_ratio= Column(String)
    average_pe= Column(String)
    sectore = Column(String)
    industry = Column(String)
    enterprise_value = Column(String)
    book_value = Column(String)
    dividend_yield = Column(String)
    promoter_holding = Column(String)
    eps = Column(String)
    sales_growth = Column(String)
    profit_growth = Column(String)
    roce = Column(String)
    cash = Column(String)
    debt = Column(String)
    roe = Column(String)
    face_value = Column(String)
    bse = Column(String)
    nse = Column(String)
    chart = Column(JSON)
    s_pros = Column(String)
    s_cons = Column(String)
    s_peer_comparison = Column(JSON)
    s_quarterly_results = Column(JSON)
    s_profit_loss = Column(JSON)
    s_balance_sheet = Column(JSON)
    s_cash_flows = Column(JSON)
    s_ratios = Column(JSON)
    s_shareholding_pattern_quarterly = Column(JSON)
    s_shareholding_pattern_yearly = Column(JSON)
    s_documents = Column(JSON)
    t_strengths = Column(String)
    t_limitations = Column(String)
    t_quarterly_results = Column(JSON)
    t_profit_loss = Column(JSON)
    t_balance_sheet_equity_and_liabilities = Column(JSON)
    t_balance_sheet_assets = Column(JSON)
    t_cash_flows = Column(JSON)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
