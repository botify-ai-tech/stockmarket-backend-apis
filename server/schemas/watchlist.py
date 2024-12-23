from typing import Dict, Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session
from server.models.ratio import Company
from server.models.watchlist import Watchlist


class WatchlistBase(BaseModel):
    id: str = None
    user_id: str = None
    company_ids: list = None


class CreateWatchlist(BaseModel):
    company_id: str


class UpdateWatchlist(WatchlistBase):
    pass


def watchlist_serializer(data: list[Watchlist], db: Session):
    if not isinstance(data, list):
        data = [data]
    if data == []:
        return []
    if data[0].company_ids == []:
        return []
    watchlists = []
    for i in data:
        companies = i.company_ids
        for j in companies:
            company_details = db.query(Company).filter(Company.id == j).first()
            company_data = {
                "id": company_details.id,
                "company_name": company_details.share_name,
                "company_symbol": company_details.share_symbol,
                "price": company_details.share_price,
                "price_per": company_details.share_price_percentage,
            }
            watchlists.append(company_data)
    return watchlists


async def validate_company(db: Session, company_id: int) -> bool:
    """Validate company exists in database."""
    return db.query(Company).filter(Company.id == company_id).first() is not None


async def get_or_create_watchlist(db: Session, user_id: int) -> Watchlist:
    """Get existing watchlist or create new one."""
    watchlist = db.query(Watchlist).filter(Watchlist.user_id == user_id).first()

    if not watchlist:
        watchlist = Watchlist(user_id=user_id, company_ids=[])
        db.add(watchlist)
        db.commit()

    return watchlist


async def toggle_company_in_watchlist(
    db: Session, watchlist: Watchlist, company_id: str
) -> Watchlist:
    """Add or remove company from watchlist."""
    company_ids = [str(id) for id in watchlist.company_ids]

    if company_id in company_ids:
        company_ids.remove(company_id)
    else:
        company_ids.append(company_id)

    watchlist.company_ids = company_ids.copy()
    db.add(watchlist)
    db.commit()
    db.refresh(watchlist)

    return watchlist
