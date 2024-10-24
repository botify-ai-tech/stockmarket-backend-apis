from pydantic import BaseModel
from typing import Optional


class ContactBase(BaseModel):
    first_name: str = None
    last_name: str = None
    email: str = None
    phone_number: str = None
    message: str = None


class CreateContact(ContactBase):
    pass


class UpdateContact(ContactBase):
    pass
