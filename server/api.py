from fastapi import APIRouter

from server.endpoints.money_control_ratio import ratio_router
from server.endpoints.backtest import backtest_router

api_router = APIRouter()
api_router.include_router(ratio_router, include_in_schema=True, prefix="/ratio")
api_router.include_router(backtest_router, include_in_schema=True, prefix="/backtest")