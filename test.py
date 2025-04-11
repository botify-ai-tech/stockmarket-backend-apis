import unicodedata
import re
from sqlalchemy import func
from server.db.base import SessionLocal
from server.models.news import NewsItem

session = SessionLocal()

def normalize_title(title: str) -> str:
    title = unicodedata.normalize("NFKD", title)
    title = title.encode("ascii", "ignore").decode("utf-8")
    title = title.lower()
    title = re.sub(r"\s+", "", title)            
    title = re.sub(r"[^\w]", "", title)          
    return title

def is_duplicate_title(title: str) -> bool:
    normalized = normalize_title(title)
    print(normalized)

    recent_news = session.query(NewsItem).order_by(NewsItem.created_at.desc()).limit(200).all()

    for news in recent_news:
        if normalize_title(news.title) == normalized:
            print(news.id)
            print(news.title)
            continue

    return False

# Example usage
title = "Trump tariff: Exporters are both, cautious and optimistic"
if is_duplicate_title(title):
    print("Duplicate")
else:
    print("New title!")
