from fastapi import APIRouter, Depends, HTTPException, Request
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

from server.utils.nifty50_stocks import NIFTY50, get_nifty_50_data

data_router = APIRouter()


@data_router.get("/top-gainer-loser")
async def top_gainer_and_loser(
    current_user: schemas.User = Depends(get_current_user),
) -> JSONResponse:
    try:
        headers = {
            "accept": "application/json, text/plain, */*",
            "accept-language": "en-US,en;q=0.9,fr;q=0.8,es;q=0.7,zh-CN;q=0.6,zh;q=0.5,hr;q=0.4,ru;q=0.3,uk;q=0.2,la;q=0.1,tr;q=0.1,ar;q=0.1,it;q=0.1,de;q=0.1,el;q=0.1,nl;q=0.1,ga;q=0.1",
            "origin": "https://www.bseindia.com",
            "priority": "u=1, i",
            "referer": "https://www.bseindia.com/",
            "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Linux"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        }
        gainer_res = requests.get(
            "https://api.bseindia.com/BseIndiaAPI/api/HoTurnover/w?flag=G",
            headers=headers,
            data={},
        )
        loser_res = requests.get(
            "https://api.bseindia.com/BseIndiaAPI/api/HoTurnover/w?flag=L",
            headers=headers,
            data={},
        )
        gainer_df = pd.DataFrame(gainer_res.json()["Table"])[
            ["ScripName", "Ltradert", "change_val", "change_percent"]
        ]
        loser_df = pd.DataFrame(loser_res.json()["Table"])[
            ["ScripName", "Ltradert", "change_val", "change_percent"]
        ].sort_values(by="change_val", ascending=True)

        gainer_df = gainer_df.sort_values(by="change_percent", ascending=False)
        loser_df = loser_df.sort_values(by="change_percent", ascending=True)

        gainers = gainer_df.to_json(orient="records")
        losers = loser_df.to_json(orient="records")
        # res = requests.get(
        #     "https://www.bseindia.com/markets/equity/EQReports/mtw_gainer_loser.aspx",
        #     headers=headers,
        # )
        # if res.status_code != 200:
        #     raise HTTPException(detail="Error fetching top gainer and losers")
        # drop_column = ["ScripCode", "Group"]
        # columns = pd.read_html(res.content)[1].iloc[0, :].to_list()
        # columns = [
        #     column.replace(" ", "").replace("%Change", "ChangePer")
        #     for column in columns
        # ]
        # df = pd.read_html(res.content)[1].iloc[1:, :]
        # df.columns = columns
        # df = df.drop(drop_column, axis=1)
        # top_gainer = df.head(10).to_json(orient="records", index=False)

        # columns = pd.read_html(res.content)[3].iloc[0, :].to_list()
        # columns = [
        #     column.replace(" ", "").replace("%Change", "ChangePer")
        #     for column in columns
        # ]
        # df2 = pd.read_html(res.content)[3].iloc[1:, :]
        # df2.columns = columns
        # df2 = df2.drop(drop_column, axis=1)
        # top_losers = df2.head(10).to_json(orient="records", index=False)

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "error": None,
                "data": {
                    "top_gainer": json.loads(gainers),
                    "top_losers": json.loads(losers),
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
        # res = NIFTY50()
        # data = res.fetch_data()
        # if data.status_code != 200:
        #     raise HTTPException(detail="Error fetching details", status_code=400)
        # data = data.json()
        data = get_nifty_50_data()
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


@data_router.get("/ipo")
def get_ipo_list(request: Request):
    try:
        filter = request.query_params.get("s", -9999)
        data = []
        if filter in ["Current", "Upcoming", "Closed"]:
            url = "https://www.chittorgarh.com/ipo/ipo_dashboard.asp"
            headers = {
                "Content-Type": "application/json",
            }
            res = requests.get(url, headers=headers)
            tables = pd.read_html(res.text)

            ipo_df = tables[0]
            columns = ipo_df.columns
            columns = [column.replace(" ", "") for column in columns]
            ipo_df.columns = columns
            ipo_df = ipo_df[ipo_df["Status"] == filter]
            data = json.loads(ipo_df.to_json(orient="records"))
        elif filter == -9999:
            url = "https://www.chittorgarh.com/ipo/ipo_dashboard.asp"
            headers = {
                "Content-Type": "application/json",
            }
            res = requests.get(url, headers=headers)
            tables = pd.read_html(res.text)

            ipo_df = tables[0]
            columns = ipo_df.columns
            columns = [column.replace(" ", "") for column in columns]
            ipo_df.columns = columns
            data = json.loads(ipo_df.to_json(orient="records"))

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "error": None,
                "data": data,
                "message": "Success",
                "status": filter,
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
