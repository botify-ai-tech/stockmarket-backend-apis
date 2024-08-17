from fastapi import APIRouter

from server.endpoints.money_control_ratio import ratio_router

api_router = APIRouter()

api_router.include_router(ratio_router, include_in_schema=True, prefix="/ratio")
