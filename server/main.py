from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# from server.config import settings
# from server.db.init_db import init_db

from .api import api_router

async def app_startup():
    try:
        pass
        # init_db()
    except Exception as e:
        # TODO: log error
        print(e)

async def lifespan(app: FastAPI):
    await app_startup()
    yield

app = FastAPI(
    title="Stock Market",
    description="Stock Market API",
    version="1.0.0",
    debug=True,
    lifespan=lifespan
)

app.include_router(api_router, prefix="/v1")

app.add_middleware(
    CORSMiddleware,
    allow_origins="*",
    allow_headers=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
)


@app.get("/")
async def welcome():
    return {"status": 200, "message": "Server running"}
