import re
import time
from sqlalchemy import desc
from datetime import datetime, timedelta

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

from fastapi.responses import JSONResponse
from fastapi import APIRouter, HTTPException

from server.db.base import Session
from server.schemas.news import News
from server.models.news import StockNews

session = Session()

news_router = APIRouter()

twenty_four_hours_ago = datetime.now() - timedelta(hours=24)


def jsonify(data):
    return {
        "user_search": data.user_search,
        "title": data.title,
        "description": data.description,
        "time_to_out_news": data.time_to_out_news,
        "feed": data.feed,
        "link": data.link,
        "similar": data.similar,
    }


@news_router.post("/news")
def globle_news(input: News):
    search = input.search
    search = re.sub(r"\s+", " ", search).strip()
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        driver = webdriver.Chrome(options=chrome_options)
        driver.get("https://pulse.zerodha.com/")

        company_name = driver.find_element(By.XPATH, "//input[@id='q']")
        company_name.send_keys(search)

        all_news_data = []

        time.sleep(3)
        html_contents = driver.find_elements(By.XPATH, "//li[@class='box item']")

        if not html_contents:
            raise Exception("No results found, Please chack your symbol and try again.")

        for html_content in html_contents:
            html_content = html_content.get_attribute("outerHTML")
            soup = BeautifulSoup(html_content, "html.parser")
            item = soup.find("li", class_="box item")
            # Extract main news

            title = item.find("h2", class_="title").get_text(strip=True)
            description = item.find("div", class_="desc").get_text(strip=True)
            time_to_out_news = item.find("span", class_="date").get_text(strip=True)
            feed = (
                item.find("span", class_="feed").get_text(strip=True).replace("— ", "")
            )
            link = item.find("h2", class_="title").a["href"]

            # Extract similar news
            similar_news = []
            try:
                for similar in item.find("ul", class_="similar").find_all("li"):
                    similar_title = similar.find("a", class_="title2").get_text(
                        strip=True
                    )
                    similar_time = similar.find("span", class_="date").get_text(
                        strip=True
                    )
                    similar_feed = (
                        similar.find("span", class_="feed")
                        .get_text(strip=True)
                        .replace("— ", "")
                    )
                    similar_link = similar.find("a", class_="title2")["href"]
                    similar_news.append(
                        {
                            "title": similar_title,
                            "time": similar_time,
                            "feed": similar_feed,
                            "link": similar_link,
                        }
                    )
            except:
                pass

            # # Construct JSON output
            # news_item = {
            #     "title": title,
            #     "description": description,
            #     "time to out this news": time_to_out_news,
            #     "feed": feed,
            #     "link": link,
            #     "similar": similar_news,
            # }

            existing_news = session.query(StockNews).filter_by(title=title).first()

            if "day ago" in time_to_out_news:
                ago_news = 24.0
            else:
                ago_news = float(time_to_out_news.replace(" hours ago", ""))

            updated_time = datetime.now() - timedelta(hours=ago_news)

            if not existing_news:
                news_entry = StockNews(
                    user_search=search,
                    title=title,
                    description=description,
                    time_to_out_news=time_to_out_news,
                    feed=feed,
                    link=link,
                    similar=similar_news,
                    created_at=updated_time,
                )
                session.merge(news_entry)
                session.commit()

            # all_news_data.append(news_item)

        data = (
            session.query(StockNews)
            .filter(
                StockNews.user_search == search,
                StockNews.created_at >= twenty_four_hours_ago,
            )
            .order_by(desc(StockNews.created_at))
            .all()
        )
        all_news_data = [jsonify(results) for results in data]

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "data": all_news_data,
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
