from fastapi import APIRouter

from server.endpoints.ratio import ratio_router
from server.endpoints.generate_summary import summary_router
# from server.endpoints.yt_to_text import yt_router
from server.endpoints.news import news_router
from  server.endpoints.user import user_router
from server.endpoints.contact import contact_router
from server.endpoints.watchlist import watchlist_router
from server.endpoints.data import data_router
from server.endpoints.bug_report import bug_report_router
from server.endpoints.contact_us import contact_us_router

api_router = APIRouter()
api_router.include_router(user_router, include_in_schema=True)
api_router.include_router(news_router, include_in_schema=True, prefix="/news", tags=["news"])
api_router.include_router(summary_router, include_in_schema=True, prefix="/summary", tags=["summary"])
api_router.include_router(ratio_router, include_in_schema=True, prefix="/ratio", tags=["ratio"])
api_router.include_router(contact_router, include_in_schema=True, prefix="/contact", tags=["contact"])
api_router.include_router(watchlist_router, include_in_schema=True, prefix="/watchlist", tags=["watchlist"])
api_router.include_router(data_router, include_in_schema=True, prefix="/data", tags=["data"])
api_router.include_router(bug_report_router, include_in_schema=True, prefix="/bug-report", tags=["bug-report"])
api_router.include_router(contact_us_router, include_in_schema=True, prefix="/contact-us", tags=["contact-us"])
# api_router.include_router(yt_router, include_in_schema=True, prefix="/youtube")