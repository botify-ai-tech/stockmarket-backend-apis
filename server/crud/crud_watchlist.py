from typing import Optional, TypeVar

from pydantic import BaseModel
from sqlalchemy.orm import Session

from server.crud.base import CRUDBase
from server.models.watchlist import Watchlist
from server.schemas.watchlist import CreateWatchlist, WatchlistBase, UpdateWatchlist

UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

# class CRUDWatchlist:

#     @staticmethod
#     def create(db: Session, obj: CreateWatchlist):
# class CRUDSUMMARY(CRUDBase[Watchlist, CreateWatchlist, CreateWatchlist]):
#     filter_options = ["amount, number of generations"]

#     def create(self, db: Session, *, obj_in: CreateWatchlist) -> Summary:
#         return super().create(db, obj_in=obj_in)

#     def update(self, db: Session, *, db_obj: Summary, obj_in: UpdateSummary) -> Summary:
#         return super().update(db, db_obj=db_obj, obj_in=obj_in)

#     def remove(self, db: Session, *, id: str) -> Optional[Summary]:
#         return super().remove(db, id=id)


# summary = CRUDSUMMARY(Summary)


class CRUDWATCHLIST(CRUDBase[Watchlist, CreateWatchlist, UpdateWatchlist]):
    filter_options = ["amount, number of generations"]

    def create(self, db: Session, *, obj_in: CreateWatchlist) -> Watchlist:
        return super().create(db, obj_in=obj_in)

    def update(
        self, db: Session, *, db_obj: Watchlist, obj_in: UpdateWatchlist
    ) -> Watchlist:
        return super().update(db, db_obj=db_obj, obj_in=obj_in)

    def remove(self, db: Session, *, id: str) -> Optional[Watchlist]:
        return super().remove(db, id=id)

    def toggle_company_in_watchlist(
        self, db: Session, db_obj: Watchlist, company_id: str
    ) -> Watchlist:
        """Add or remove company from watchlist."""
        company_ids = [str(id) for id in db_obj.company_ids]
        flag = True
        if company_id in company_ids:
            company_ids.remove(company_id)
            flag = False
        else:
            company_ids.append(company_id)

        db_obj.company_ids = company_ids.copy()
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

        return db_obj, flag

    def get_or_create_watchlist(self, db: Session, user_id: str) -> Watchlist:
        """Get existing watchlist or create new one."""
        db_obj = db.query(Watchlist).filter(Watchlist.user_id == user_id).first()

        if not db_obj:
            db_obj = Watchlist(user_id=user_id, company_ids=[])
            db.add(db_obj)
            db.commit()

        return db_obj


watchlist = CRUDWATCHLIST(Watchlist)
