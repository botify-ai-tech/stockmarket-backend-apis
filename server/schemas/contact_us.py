from pydantic import BaseModel
from typing import Optional

class ContactUsInput(BaseModel):
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    message: Optional[str] = None


class ContactUsOutput(BaseModel):
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    message: Optional[str] = None
    class Config:
        orm_mode = True