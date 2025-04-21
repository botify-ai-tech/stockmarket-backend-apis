from typing import List, Optional
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from server.endpoints.deps import get_db
from server.schemas.news_letter import NewsLetterInput, NewsLetterOutput
from server.models.news_letter import NewsLetter
from fastapi import status
from sqlalchemy.exc import IntegrityError

news_letter_router = APIRouter()

@news_letter_router.post("",response_model=NewsLetterOutput)
async def create_news_letter(
    request_data:NewsLetterInput,
    db: Session = Depends(get_db)
):

    try:

        email_data = db.query(NewsLetter).filter(NewsLetter.email == request_data.email).first()

        if email_data:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email address is already subscribed."
            )

        
        new_news_letter = NewsLetter(
            email=request_data.email,
        )

        db.add(new_news_letter)
        db.commit()
        db.refresh(new_news_letter)

        return JSONResponse(
            status_code=201,
            content= {
                "success":True,
                "error": None,
                "data" : {
                    'email':new_news_letter.email,
                },
                "message":'news letter created.'
            }
        )

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email address is already subscribed."
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
                "message": "Something went wrong!",
            },
        )

@news_letter_router.get("", response_model=List[NewsLetterOutput])
async def get_news_letter(
    db: Session = Depends(get_db) , skip: Optional[int] = 0, limit: Optional[int] = 10):

    
    try:
        news_letters = db.query(NewsLetter).order_by(NewsLetter.created_at.desc()).offset(skip).limit(limit).all()
        total_count = db.query(NewsLetter).count()
    
        if not news_letters:
            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "data": [],
                    "error": "No news letters found",
                    "message": "No news letters found"
                },
            )
        
        news_letter_list = [
            {
                "id": news_letter.id,
                'email':news_letter.email,
            }
            for news_letter in news_letters
        ]

        return JSONResponse(
            status_code=200,
            content= {
                    "success":True,
                    "error": None,
                    "data" :{
                        "news_letters":news_letter_list,
                        "total_count":total_count,
                    },
                    "message":'news letter fetched.'
                }
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
                "message": "Something went wrong!",
            },
        )
