from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class BugReportOutput(BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None
    full_name: Optional[str] = None
    photo: Optional[str] = None
    message: str

    class Config:
        orm_mode = True