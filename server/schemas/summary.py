from typing import Dict
from pydantic import BaseModel


class SummaryBase(BaseModel):
    id: str = None
    user_id: str = None
    summary: Dict  = None
    filename: str = None


class CreateSummary(SummaryBase):
    pass


class UpdateSummary(SummaryBase):
    pass
