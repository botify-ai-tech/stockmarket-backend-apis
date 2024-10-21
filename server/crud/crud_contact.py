from typing import Optional, TypeVar

from pydantic import BaseModel
from sqlalchemy import and_, desc, or_
from sqlalchemy.orm import Session

from server.crud.base import CRUDBase
from server.models.contact import Contact
from server.models.user import User
from server.schemas.contact import CreateContact, UpdateContact

UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDCONTACT(CRUDBase[Contact, CreateContact, UpdateContact]):
    filter_options = ["amount, number of generations"]

    def create(self, db: Session, *, obj_in: CreateContact) -> Contact:
        return super().create(db, obj_in=obj_in)

    def update(self, db: Session, *, db_obj: Contact, obj_in: UpdateContact) -> Contact:
        return super().update(db, db_obj=db_obj, obj_in=obj_in)

    def remove(self, db: Session, *, id: str) -> Optional[Contact]:
        return super().remove(db, id=id)

    def get_contact_by_user_id(
        self, db: Session, user_id: str, skip: int = 0, limit: int = 10
    ) -> Contact:
        return (
            db.query(Contact)
            .filter(Contact.user_id == user_id)
            .order_by(desc(Contact.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_contact_count(self, db: Session, user_id: str) -> Contact:
        return db.query(Contact).filter(Contact.user_id == user_id).count()

    def get_search_query(
        self, db: Session, search: str, skip: int = 0, limit: int = 10
    ) -> Contact:
        return (
            db.query(Contact, User)
            .join(User.disabled == False, User.is_active == True)
            .filter(
                and_(
                    or_(
                        Contact.name.ilike(f"%{search}%"),
                        Contact.email.ilike(f"%{search}%"),
                    ),
                )
            )
            .offset(skip)
            .limit(limit)
            .all()
        )


contact = CRUDCONTACT(Contact)
