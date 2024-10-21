from typing import Optional, TypeVar

from pydantic import BaseModel
from sqlalchemy.orm import Session

from server.crud.base import CRUDBase
from server.models.ratio import Ratio
from server.schemas.ratio import CreateRatio, UpdateRatio

UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDRATIO(CRUDBase[Ratio, CreateRatio, UpdateRatio]):
    filter_options = ["amount, number of generations"]

    def create(self, db: Session, *, obj_in: CreateRatio) -> Ratio:
        return super().create(db, obj_in=obj_in)

    def update(self, db: Session, *, db_obj: Ratio, obj_in: UpdateRatio) -> Ratio:
        return super().update(db, db_obj=db_obj, obj_in=obj_in)

    def remove(self, db: Session, *, id: str) -> Optional[Ratio]:
        return super().remove(db, id=id)
    
    def get_by_nifty_share(self, db: Session, nifty_sahre: str) -> Optional[Ratio]:
        return db.query(Ratio).filter(Ratio.nifty_sahre == nifty_sahre).first() 


ratio = CRUDRATIO(Ratio)
