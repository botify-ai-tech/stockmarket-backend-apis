from typing import Dict, Optional
from pydantic import BaseModel


class SummaryBase(BaseModel):
    id: str = None
    user_id: str = None
    summary: Dict  = None
    filename: Optional[str] = None
    url: Optional[str] = None


class CreateSummary(SummaryBase):
    pass


class UpdateSummary(SummaryBase):
    pass
