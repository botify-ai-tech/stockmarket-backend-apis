from typing import Optional

from pydantic import BaseModel


class RatioBase(BaseModel):
    symbol: str

    class Config:
        from_attributes = True