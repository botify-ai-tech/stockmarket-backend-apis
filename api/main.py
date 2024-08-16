from fastapi import FastAPI

# from src.api.user.router import router as user_router

app = FastAPI()

app.include_router(None, prefix="/users", tags=["users"])