from typing import Optional, TypeVar

from pydantic import BaseModel
from sqlalchemy.orm import Session

from server.crud.base import CRUDBase
from server.models.summary import Summary
from server.schemas.summary import CreateSummary, UpdateSummary

UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDSUMMARY(CRUDBase[Summary, CreateSummary, UpdateSummary]):
    filter_options = ["amount, number of generations"]

    def create(self, db: Session, *, obj_in: CreateSummary) -> Summary:
        return super().create(db, obj_in=obj_in)

    def update(self, db: Session, *, db_obj: Summary, obj_in: UpdateSummary) -> Summary:
        return super().update(db, db_obj=db_obj, obj_in=obj_in)

    def remove(self, db: Session, *, id: str) -> Optional[Summary]:
        return super().remove(db, id=id)


summary = CRUDSUMMARY(Summary)
