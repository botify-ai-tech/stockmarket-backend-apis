import re
from datetime import datetime, timedelta
from typing import Optional


from fastapi.responses import JSONResponse
from fastapi import APIRouter, HTTPException, Depends

from server.db.base import SessionLocal
from server.schemas.news import News
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
        "small_description": data.small_description,
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
        "image": data.image,
        "created_at": str(data.created_at),
        "updated_at": str(data.updated_at),
    }


@news_router.post("/publice-news")
def globle_news(
    search: str = None,
    skip: Optional[int] = 0,
    limit: Optional[int] = 10,
    db: Session = Depends(get_db),
):
    try:
        if search:
            search = re.sub(r"\s+", " ", search).strip() if search else ""
            existing_news = crud.news.get_new_search_query(db, search, skip, limit)
            total_news = crud.news.get_total_new_search_query(db, search)
        else:
            existing_news = crud.news.get_new_without_search_query(db, skip, limit)
            total_news = crud.news.get_total_news_without_search_query(db)

        all_news_data_ = [jsonify(results) for results in existing_news]
        all_news_data = sorted(
            all_news_data_, key=lambda x: x["created_at"], reverse=True
        )

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
                    "message": "The news has been removed from your saved list.",
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
                    "message": "News added to your saved list.",
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
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    skip: int = 0,
    limit: int = 10,
):
    news_saves, count = crud.news_save.get_news_id(db, current_user.id, skip, limit)
    news_ids = [news_save.news_id for news_save in news_saves]

    if not news_ids:
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "data": [],
                "error": "No saved news found.",
                "message": "User has not saved any news.",
            },
        )

    saved_news = crud.news.saved_news(db, news_ids=news_ids)

    if not saved_news:
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "data": [],
                "error": "No saved news found for this user.",
                "message": "No saved news found.",
            },
        )

    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "data": [jsonify(news) for news in saved_news],
            "total_news" : count,
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
        crud.news.remove(db, news_item.id)

    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "message": f"Deleted {len(news_to_delete)} old news item(s) successfully.",
            "deleted_count": len(news_to_delete),
        },
    )
