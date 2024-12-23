from typing import Optional, TypeVar

from pydantic import BaseModel
from operator import or_
from sqlalchemy.orm import Session

from server.crud.base import CRUDBase
from server.models.ratio import Ratio, Company, Assessment
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

    def get_ratio_analysis(self, db: Session, symbol: str) -> Optional[Ratio]:
        return db.query(Ratio).filter(Ratio.share_symbol == symbol).first()

    def get_by_symbol(self, db: Session, share_symbol: str) -> Optional[Assessment]:
        return (
            db.query(Assessment).filter(Assessment.share_symbol == share_symbol).all()
        )

    def get_by_company_details(
        self, db: Session, share_symbol: str
    ) -> Optional[Company]:
        return db.query(Company).filter(Company.share_symbol == share_symbol).first()
    
    def get_by_company_id(
        self, db: Session, id: str
    ) -> Optional[Company]:
        return db.query(Company).filter(Company.id == id).first()

    def get_all_companies(
        self, db: Session, skip: int = 0, limit: int = 10, search: str = None
    ) -> Optional[Company]:
        if search:
            return (
                db.query(Company)
                .filter(
                    or_(
                        or_(
                            Company.share_name.ilike(f"%{search}%"),
                            Company.sectore.ilike(f"%{search}%"),
                        ),
                        Company.share_symbol.ilike(f"%{search}%"),
                    ),
                    )
                .offset(skip)
                .limit(limit)
                .all()
            )
        return db.query(Company).offset(skip).limit(limit).all()
    

    def get_total_companies(
        self, db: Session, search: str = None
    ) -> Optional[Company]:
        if search:
            return (
                db.query(Company)
                .filter(
                    or_(
                        or_(
                            Company.share_name.ilike(f"%{search}%"),
                            Company.sectore.ilike(f"%{search}%"),
                        ),
                        Company.share_symbol.ilike(f"%{search}%"),
                    ),
                    )
                .count()
            )
        return db.query(Company).count()



ratio = CRUDRATIO(Ratio)
