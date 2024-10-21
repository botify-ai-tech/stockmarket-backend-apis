from typing import List, Optional, TypeVar

from pydantic import BaseModel
from sqlalchemy.orm import Session

from server.crud.base import CRUDBase
from server.models.user import User
from server.schemas.user import UserCreate, UserUpdate

UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDUSER(CRUDBase[User, UserCreate, UserUpdate]):
    filter_options = ["amount, number of generations"]

    def get_all(self, db: Session) -> List[User]:
        return db.query(User).all()

    def get_by_id(self, db: Session, *, id: str) -> User:
        return db.query(User).filter(User.id == id).first()

    def get_by_fb_uid(self, db: Session, *, firebase_id: str) -> User:
        return db.query(User).filter(User.firebase_id == firebase_id).first()

    def get_by_email(self, db: Session, *, email: str) -> User:
        return db.query(User).filter(User.email == email).first()

    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        return super().create(db, obj_in=obj_in)

    def update(self, db: Session, *, db_obj: User, obj_in: UserUpdate) -> User:
        return super().update(db, db_obj=db_obj, obj_in=obj_in)

    def remove(self, db: Session, *, id: str) -> Optional[User]:
        return super().remove(db, id=id)
    
    def verify_user(self, db: Session, email: str) -> User:
        return db.query(User).filter(User.email == email, User.disabled == False).first()
    
    def get_by_user(self, db: Session, id: str) -> User:
        return db.query(User).filter(User.id == id, User.disabled == False, User.is_active == True).first()
    


user = CRUDUSER(User)
