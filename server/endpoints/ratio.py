from fastapi.responses import JSONResponse
from requests import Session

from fastapi import APIRouter, Depends, HTTPException
from ratio import money_con_ration
from server import crud, schemas
from server.endpoints.deps import get_db
from server.utils.auth import get_current_user
from dotenv import load_dotenv

load_dotenv()


ratio_router = APIRouter()


@ratio_router.post("/companies")
def symbols(db: Session = Depends(get_db), current_user=Depends(get_current_user)):

    with open("nifty.txt", "r") as f:
        companies = f.readlines()

    company = [com.strip() for com in companies]

    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "error": None,
            "data": company,
            "message": "Ratio data scrape successfully.",
        },
    )


@ratio_router.post("/ratio-analysis")
def get_company_symbol(
    data: schemas.Symbol,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        company = data.company_name
        ratio_details = crud.ratio.get_by_nifty_share(db, company)

        response = {
            "stock_name": ratio_details.stock_name,
            "Evaluation": {
                "favourable_indicators": ratio_details.favourable_indicators,
                "unfavourable_indicators": ratio_details.unfavourable_indicators,
            },
            "overall_picture": {
                "summary": ratio_details.summary,
                "pros": ratio_details.pros,
                "cons": ratio_details.cons,
            },
            "investment_recommendation": ratio_details.investment_recommendation,
        }

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "error": None,
                "data": response,
                "message": "Stock detail analasy successfully. ",
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
                "message": "Something went wrong!",
            },
        )
    finally:
        db.close()


@ratio_router.post("/ratio-cronjob")
def ratio_cronjob(db: Session = Depends(get_db)):

    money_con_ration(db)

    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "error": None,
            "data": None,
            "message": "Ratio data scrape successfully.",
        },
    )
