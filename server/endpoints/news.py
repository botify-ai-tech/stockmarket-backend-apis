import re
from datetime import datetime, timedelta
from typing import Optional


from fastapi.responses import JSONResponse
from fastapi import APIRouter, HTTPException, Depends

from server.db.base import SessionLocal
from server.schemas.news import News
from server.models.news import NewsItem
from sqlalchemy import or_
from sqlalchemy.orm import Session
from server.endpoints.deps import get_db
from server import crud, schemas
from server.utils.auth import get_current_user


session = SessionLocal()

news_router = APIRouter()

twenty_four_hours_ago = datetime.now() - timedelta(hours=24)


def jsonify(data):
    return {
        "id": data.id,
        "title": data.title,
        "published_date": data.published_date,
        "company_name": data.company_name,
        "stock_name": data.stock_name,
        "description": data.description,
        "time_to_out_news": data.time_to_out_news,
        "feed": data.feed,
        "link": data.other_news_link,
        "sectors": data.sectors,
        "category": data.category,
        "similar": data.similar,
        "classification": data.classification,
        "type_of_impact": data.type_of_impact,
        "Country": data.Country,
        "scale_of_impact": data.scale_of_impact,
        "timeframe_of_impact": data.timeframe_of_impact,
        "investor_sentiment": data.investor_sentiment,
        "market_volatility": data.market_volatility,
        "detailed_explanation": data.detailed_explanation,
    }


@news_router.post("/publice-news")
def globle_news(search: str = None, sector: str = None, skip: Optional[int] = 0,db: Session = Depends(get_db)):

    try:
        if not search:
            existing_news = crud.news.get_new_without_search_query(db, skip)
            total_news = crud.news.get_total_news_without_search_query(db)
        else:
            search = re.sub(r"\s+", " ", search).strip() if search else ""
            sectors = re.sub(r"\s+", " ", sector).strip() if sector else ""
            existing_news = crud.news.get_new_search_query(db, search, sectors, skip)
            total_news = crud.news.get_total_new_search_query(db, search, sectors)

        all_news_data = [jsonify(results) for results in existing_news]

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "data": ({"news": all_news_data, "total_news": total_news}),
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


@news_router.post("/news")
def globle_news(
    input: News, db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    try:
        news = crud.news.get_by_id(db, id=input.id)
        if not news:
            raise HTTPException(status_code=404, detail="News not found.")

        existing_save = crud.news_save.existing_save(db, current_user.id, news.id)
        if existing_save:
            crud.news_save.remove(db, id=existing_save.id)

            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "error": None,
                    "data": None,
                    "message": "News unsaved.",
                },
            )

        else:
            crud.news_save.create(
                db, obj_in=schemas.NewsSave(user_id=current_user.id, news_id=input.id)
            )

            save_news = crud.news.get_by_id(db, id=input.id)

            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "error": None,
                    "data": jsonify(save_news),
                    "message": "News saved successfully",
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


@news_router.post("/get-all-save-news")
def get_all_save_news(
    db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    news_saves = crud.news_save.get_news_id(db, current_user.id)
    news_ids = [news_save.news_id for news_save in news_saves]

    if not news_ids:
        return JSONResponse(
            status_code=404,
            content={
                "success": False,
                "data": None,
                "error": "No saved news found.",
                "message": "User has not saved any news.",
            },
        )

    saved_news = crud.news.saved_news(db, news_ids=news_ids)

    if not saved_news:
        return JSONResponse(
            status_code=404,
            content={
                "success": False,
                "data": None,
                "error": "No saved news found for this user.",
                "message": "No saved news found.",
            },
        )

    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "data": [jsonify(news) for news in saved_news],
            "error": None,
            "message": "Saved news fetched successfully.",
        },
    )


@news_router.delete("/delete-old-news")
def delete_old_news(db: Session = Depends(get_db)):

    old_news_items = crud.news.get_48_old_news(db)

    if not old_news_items:
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "No news older than 48 hours found.",
                "deleted_count": 0,
            },
        )

    saved_news_ids = crud.news_save.get_save_news_id(db)
    saved_news_ids = [news_id[0] for news_id in saved_news_ids]

    news_to_delete = [news for news in old_news_items if news.id not in saved_news_ids]

    if not news_to_delete:
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "All old news are saved, no news deleted.",
                "deleted_count": 0,
            },
        )

    for news_item in news_to_delete:
        crud.news.remove(news_item)

    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "message": f"Deleted {len(news_to_delete)} old news item(s) successfully.",
            "deleted_count": len(news_to_delete),
        },
    )
