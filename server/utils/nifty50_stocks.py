import requests


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
