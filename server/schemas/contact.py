from pydantic import BaseModel
from typing import Optional


class ContactBase(BaseModel):
    id: str = None 
    user_id: str = None
    name: str = None
    email: str = None
    phone_number: str = None
    message: str = None


class CreateContact(ContactBase):
    pass


class UpdateContact(ContactBase):
    pass
