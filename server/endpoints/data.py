from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from server import crud
from sqlalchemy.orm import Session
from server import schemas
from server.schemas.watchlist import (
    watchlist_serializer,
)
from server.utils.auth import get_current_user
from server.endpoints.deps import get_db
import requests
import pandas as pd
import json

from server.utils.nifty50_stocks import NIFTY50

data_router = APIRouter()


@data_router.get("/top-gainer-loser")
async def top_gainer_and_loser(
    current_user: schemas.User = Depends(get_current_user),
) -> JSONResponse:
    try:
        headers = {"user-agent": "PostmanRuntime/7.43.0"}
        res = requests.get(
            "https://www.bseindia.com/markets/equity/EQReports/mtw_gainer_loser.aspx",
            headers=headers,
        )
        if res.status_code != 200:
            raise HTTPException(detail="Error fetching top gainer and losers")
        drop_column = ["ScripCode", "Group"]
        columns = pd.read_html(res.content)[1].iloc[0, :].to_list()
        columns = [
            column.replace(" ", "").replace("%Change", "ChangePer")
            for column in columns
        ]
        df = pd.read_html(res.content)[1].iloc[1:, :]
        df.columns = columns
        df = df.drop(drop_column, axis=1)
        top_gainer = df.head(10).to_json(orient="records", index=False)

        columns = pd.read_html(res.content)[3].iloc[0, :].to_list()
        columns = [
            column.replace(" ", "").replace("%Change", "ChangePer")
            for column in columns
        ]
        df2 = pd.read_html(res.content)[3].iloc[1:, :]
        df2.columns = columns
        df2 = df2.drop(drop_column, axis=1)
        top_losers = df2.head(10).to_json(orient="records", index=False)

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "error": None,
                "data": {
                    "top_gainer": json.loads(top_gainer),
                    "top_losers": json.loads(top_losers),
                },
                "message": "Success",
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


@data_router.get("/nifty-50")
async def nifty_50_all_stocks() -> JSONResponse:

    try:
        res = NIFTY50()
        data = res.fetch_data()
        if data.status_code != 200:
            raise HTTPException(detail="Error fetching details", status_code=400)
        data = data.json()

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "error": None,
                "data": data,
                "message": "Success",
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
