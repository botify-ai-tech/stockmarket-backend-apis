import re
import time
from sqlalchemy import desc
from datetime import datetime, timedelta

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

from fastapi.responses import JSONResponse
from fastapi import APIRouter, HTTPException

from server.db.base import Session
from server.schemas.news import News
from server.models.news import StockNews
from sqlalchemy import or_


session = Session()

news_router = APIRouter()

twenty_four_hours_ago = datetime.now() - timedelta(hours=24)


def jsonify(data):
    return {
        "title": data.title,
        "company_name": data.company_name,
        "stock_name": data.stock_name,
        "description": data.description,
        "time_to_out_news": data.time_to_out_news,
        "feed": data.feed,
        "link": data.link,
        "sectors": data.sectors,
        "category": data.category,
        "similar": data.similar,
    }


@news_router.post("/news")
def globle_news(input: News):
    search = input.search
    search = re.sub(r"\s+", " ", search).strip()

    try:
        existing_news = (
            session.query(StockNews)
            .filter(
                or_(
                    StockNews.company_name.ilike(f"{search}%"),
                    StockNews.company_name.ilike(f"%{search}"),
                )
            )
            .all()
        )
        all_news_data = [jsonify(results) for results in existing_news]

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "data": all_news_data,
                "error": None,
                "message": "News fetched successfully.",
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "data": None,
                "error": str(e),
                "message": "Something went wrong!",
            },
        )
