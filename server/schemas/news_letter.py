from pydantic import BaseModel, EmailStr
from typing import Optional

class NewsLetterInput(BaseModel):
    email: EmailStr = None

class NewsLetterOutput(BaseModel):
    email: EmailStr = None
    
    class Config:
        orm_mode = True