from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from server.endpoints.deps import get_db
from server.utils.auth import get_current_user
from ratio.scrap_daily_spec_ratio import daily_spec_scraper
from ratio.scrap_quarterly_ratios import scrape_quarterly


admin_router = APIRouter()

# update daily key metrics
@admin_router.post("/update-daily-metrics")
def update_daily_key_metrics(

    start : int,
    end : int,
    db: Session = Depends(get_db),
    # current_user=Depends(get_current_user)
):
    try :
        response = daily_spec_scraper(start=start,end=end)

        if response.get("unscraped_companies"):
            with open("unscraped_stock.txt", "a") as file:
                file.write("\n".join(response["unscraped_companies"]) + "\n")


        if "error" in response and response["error"]:
            return JSONResponse(
                status_code=200,
                content={
                    "success": False, 
                    "error": response.get("error"),
                    "data": None,
                    "message": response.get("details", "Stocks not updated successfully.")
                },
            )

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "error": None,
                "data": response,
                "message": "stocks update successfully.",
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



# update All Data Quarterly 
@admin_router.post("/update-share-quarterly")
def update_quaterly_key_metrics(
    start : int,
    end : int,
    db: Session = Depends(get_db),
    # current_user=Depends(get_current_user)
):
    try :
        response = scrape_quarterly(start=start,end=end)

        if "error" in response and response["error"]:
            return JSONResponse(
                status_code=200,
                content={
                    "success": False, 
                    "error": response.get("error"),
                    "data": None,
                    "message": response.get("details", "Stocks not updated successfully.")
                },
            )
        
        if response.get("unscraped_companies"):
            with open("unscraped_stock.txt", "a") as file:
                file.write("\n".join(response["unscraped_companies"]) + "\n")

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "error": None,
                "data": response,
                "message": "stocks update successfully.",
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