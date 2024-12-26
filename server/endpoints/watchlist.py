from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from server import crud
from sqlalchemy.orm import Session
from server import schemas
from server.models.ratio import Company
from server.schemas.watchlist import (
    get_or_create_watchlist,
    toggle_company_in_watchlist,
    validate_company,
    watchlist_serializer,
)
from server.utils.auth import get_current_user
from firebase_admin import credentials
from server.endpoints.deps import get_db
from server.models.watchlist import Watchlist

watchlist_router = APIRouter()


@watchlist_router.post(
    "",
    response_model=dict,
    summary="Create or update user watchlist",
    description="Add or remove a company from user's watchlist. Creates new watchlist if none exists.",
)
async def create_and_update_watchlist(
    data: schemas.CreateWatchlist,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
) -> JSONResponse:
    """
    Handles creation and updating of user watchlists.

    Args:
        data: CreateWatchlist schema containing company_id
        db: Database session
        current_user: Currently authenticated user

    Returns:
        JSONResponse with watchlist data or error details

    Raises:
        HTTPException: If company not found or other validation errors
    """
    try:
        # Validate company exists
        if not crud.ratio.get_by_company_id(db, data.company_id):
            raise HTTPException(
                status_code=404, detail=f"Company with id {data.company_id} not found"
            )
        # Get or create watchlist
        watchlist = crud.watchlist.get_or_create_watchlist(db, current_user.id)

        # Toggle company in watchlist
        updated_watchlist, flag = crud.watchlist.toggle_company_in_watchlist(
            db, watchlist, data.company_id
        )

        # Serialize and return response
        watchlist_data = watchlist_serializer(updated_watchlist, db)

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "error": None,
                "data": watchlist_data,
                "message": (
                    "Success! The company is now in your watchlist.!!"
                    if flag
                    else "Success! The company has been removed from your watchlist.!!"
                ),
            },
        )

    except HTTPException as e:
        db.rollback()
        return JSONResponse(
            status_code=e.status_code,
            content={
                "success": False,
                "data": None,
                "error": str(e.detail),
                "message": str(e.detail),
            },
        )
    except Exception as e:
        db.rollback()
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "data": None,
                "error": str(e),
                "message": "Something went wrong! The company couldn't be added to your watchlist.!!",
            },
        )
    finally:
        db.close()


@watchlist_router.get(
    "",
    response_model=dict,
    summary="Get user watchlist",
)
async def create_and_update_watchlist(
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
) -> JSONResponse:
    try:
        watchlist = crud.watchlist.get_or_create_watchlist(
            db=db, user_id=current_user.id
        )
        watchlist_data = []
        if watchlist:
            watchlist_data = watchlist_serializer(watchlist, db)
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "error": None,
                "data": watchlist_data,
                "message": "Success! The company is now in your watchlist.!!",
            },
        )

    except HTTPException as e:
        return JSONResponse(
            status_code=e.status_code,
            content={
                "success": False,
                "data": None,
                "error": str(e.detail),
                "message": str(e.detail),
            },
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "data": None,
                "error": str(e),
                "message": "Something went wrong! The company couldn't be added to your watchlist.!!",
            },
        )
    finally:
        db.close()
