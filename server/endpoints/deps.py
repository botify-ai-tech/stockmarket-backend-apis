from typing import Generator

from fastapi import Header, HTTPException
from fastapi.security import HTTPBasic

from server.config import settings
from server.db.base import SessionLocal

security = HTTPBasic()


def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


async def get_token_header(x_token: str = Header(...)):
    if x_token != settings.AUTH_TOKEN:
        raise HTTPException(status_code=400, detail="X-Token header invalid")