from pydantic import BaseModel
from typing import Optional


class News(BaseModel):
    id: str

class CreateNews(BaseModel):
    title: Optional[str]
    published_date: Optional[str]
    summary: Optional[str]
    classification: Optional[str]
    type_of_impact: Optional[str]
    description: Optional[str]
    sectors: Optional[str]
    category: Optional[str]
    Country: Optional[str]
    company_name: Optional[str]
    stock_name: Optional[str]
    scale_of_impact: Optional[str]
    timeframe_of_impact: Optional[str]
    investor_sentiment: Optional[str]
    market_volatility: Optional[str]
    detailed_explanation: Optional[str]
    time_to_out_news: Optional[str]
    feed: Optional[str]
    other_news_link: Optional[str]
    similar: Optional[str]
    created_at: Optional[str]
    is_save: Optional[str]
    image: Optional[str]

class UpdateNews():
    pass