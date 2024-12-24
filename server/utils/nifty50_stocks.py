import time
import requests
import json


class NIFTY50:
    def __init__(self, timeout=120) -> None:
        self.__url = "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%2050"
        self.__session = requests.sessions.Session()
        self.__session.headers = {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.5",
        }
        self.__timeout = timeout
        self.__session.get(
            "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%2050",
            timeout=self.__timeout,
        )

    def fetch_data(self):
        try:
            data = self.__session.get(url=self.__url, timeout=self.__timeout)
            return data
        except Exception as ex:
            self.__session.get(
                "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%2050",
                timeout=self.__timeout,
            )


async def get_nifty_50_data():
    PRICE_SYMBOL_LIST = [
        [
            "RELIANCE",
            "TCS",
            "HDFCBANK",
            "ICICIBANK",
            "BHARTIARTL",
            "INFY",
            "SBIN",
            "ITC",
            "HINDUNILVR",
            "HCLTECH",
            "LT",
            "SUNPHARMA",
            "BAJFINANCE",
        ],
        [
            "M&M",
            "KOTAKBANK",
            "MARUTI",
            "AXISBANK",
            "ULTRACEMCO",
            "NTPC",
            "WIPRO",
            "ONGC",
            "TITAN",
            "POWERGRID",
            "ADANIENT",
            "TATAMOTORS",
        ],
        [
            "ADANIPORTS",
            "BAJAJFINSV",
            "TRENT",
            "BAJAJ-AUTO",
            "COALINDIA",
            "JSWSTEEL",
            "ASIANPAINT",
            "BEL",
            "NESTLEIND",
            "TATASTEEL",
            "TECHM",
            "GRASIM",
        ],
        [
            "HINDALCO",
            "SBILIFE",
            "HDFCLIFE",
            "EICHERMOT",
            "BPCL",
            "CIPLA",
            "BRITANNIA",
            "DRREDDY",
            "SHRIRAMFIN",
            "APOLLOHOSP",
            "TATACONSUM",
            "HEROMOTOCO",
            "INDUSINDBK",
        ],
    ]

    url = "https://groww.in/v1/api/stocks_data/v1/tr_live_delayed/segment/CASH/latest_aggregated"
    all_data = {}
    for symbols in PRICE_SYMBOL_LIST:
        payload = json.dumps(
            {
                "exchangeAggReqMap": {
                    "NSE": {"priceSymbolList": symbols, "indexSymbolList": []},
                    "BSE": {"priceSymbolList": [], "indexSymbolList": []},
                }
            }
        )
        headers = {
            "Content-Type": "application/json",
            # 'Cookie': '_cfuvid=m8wzti1dk4baeQ1hBlAdqdKzAuhHCbM2oAIxDFR96PM-1735030165293-0.0.1.1-604800000'
        }

        response = await requests.request("POST", url, headers=headers, data=payload)
        if response.status_code != 200:
            continue
        data = response.json()

        symbol_data = data["exchangeAggRespMap"]["NSE"]["priceLivePointsMap"]
        all_data.update(symbol_data)
        time.sleep(0.6)

    final_data = []
    for data in list(all_data.values()):
        final_data.append(
            {
                "companyName": data.get("symbol"),
                "lastPrice": round(data.get("ltp"), 2),
                "pChange": round(data.get("dayChangePerc"), 2),
                "change": round(data.get("dayChange"), 2),
            }
        )
    return final_data
