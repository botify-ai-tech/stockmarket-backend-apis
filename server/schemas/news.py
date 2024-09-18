from pydantic import BaseModel


class News(BaseModel):
    search: str

    class Config:
        from_attributes = True