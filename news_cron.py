import json
import os
import regex as re
import time
from dotenv import load_dotenv
from datetime import datetime, timedelta

from bs4 import BeautifulSoup
import requests

from fastapi.responses import JSONResponse
from fastapi import HTTPException

from server.utils.prompt import gemini_prompt
from server.db.base import SessionLocal
from server.models.news import NewsItem

import google.generativeai as genai

load_dotenv()

gemini_ai_key = os.getenv("GEMINI_AI_KEY")
genai.configure(api_key=gemini_ai_key)

session = SessionLocal()

twenty_four_hours_ago = datetime.now() - timedelta(hours=24)


def globle_news():
    # try:
    response = requests.get("https://pulse.zerodha.com/")
    if response.status_code != 200:
        raise Exception(
            "Failed to load page. Status code: {}".format(response.status_code)
        )

    soup = BeautifulSoup(response.content, "html.parser")

    html_contents = soup.find_all("li", class_="box item")

    if not html_contents:
        raise HTTPException(
            status_code=404, detail="No data found, Please try again after some time."
        )

    # news_items = []
    start_news = 0
    for item in html_contents:

        title = item.find("h2", class_="title").get_text(strip=True)
        description = item.find("div", class_="desc").get_text(strip=True)
        time_to_out_news = item.find("span", class_="date").get_text(strip=True)
        feed = item.find("span", class_="feed").get_text(strip=True).replace("— ", "")
        link = item.find("h2", class_="title").a["href"]

        similar_news = []
        similar_list = item.find("ul", class_="similar")
        if similar_list:
            for similar in similar_list.find_all("li"):
                try:
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
                    continue

        news_item = {
            "title": title,
            "description": description,
            "time to out this news": time_to_out_news,
            "feed": feed,
            "link": link,
            "similar": similar_news,
        }
        existing_news = session.query(NewsItem).filter_by(title=title).first()
        if existing_news:
            continue

        retries = 3  # Retry up to 3 times
        success = False

        while retries > 0 and not success:
            try:
                time.sleep(4)

                prompt = gemini_prompt(news_item)
                model = genai.GenerativeModel("gemini-1.5-flash")
                analysis = model.generate_content(prompt)
                print("data is provieded by Gemini AI")

                ai_data = analysis.text
                pattern = r"""\{(?:[^{}]|(?R))*\}"""

                matches = re.findall(pattern, ai_data, re.DOTALL)[0]
                data = json.loads(matches)

                title = data["article"]["title"] if data["article"]["title"] else ""
                published_date = (
                    data["article"]["published_date"]
                    if data["article"]["published_date"]
                    else ""
                )
                summary = (
                    data["article"]["summary"] if data["article"]["summary"] else ""
                )
                classification = (
                    data["classification"]["primary_class"]
                    if data["classification"]["primary_class"]
                    else ""
                )
                type_of_impact = (
                    data["impact_analysis"]["type_of_impact"]
                    if data["impact_analysis"]["type_of_impact"]
                    else ""
                )
                impact_description = (
                    data["impact_analysis"]["majority_market_impact"][
                        "impact_description"
                    ]
                    if data["impact_analysis"]["majority_market_impact"][
                        "impact_description"
                    ]
                    else ""
                )
                sectors_impacted = (
                    data["impact_analysis"]["sectors_impacted"]["sector_list"]
                    if data["impact_analysis"]["sectors_impacted"]["sector_list"]
                    else ""
                )
                category_impacted = (
                    data["category_impacted"]["category_list"]
                    if data["category_impacted"]["category_list"]
                    else ""
                )
                Country = (
                    data["Country"]["country_name"]
                    if data["Country"]["country_name"]
                    else ""
                )
                company_name = (
                    data["company_name"]["company_name"]
                    if data["company_name"]["company_name"]
                    else ""
                )
                stocks_impacted = (
                    data["impact_analysis"]["stocks_impacted"]["stock_list"]
                    if data["impact_analysis"]["stocks_impacted"]["stock_list"]
                    else ""
                )
                scale_of_impact = (
                    data["impact_explanation"]["scale_of_impact"]
                    if data["impact_explanation"]["scale_of_impact"]
                    else ""
                )
                timeframe_of_impact = (
                    data["impact_explanation"]["timeframe_of_impact"]
                    if data["impact_explanation"]["timeframe_of_impact"]
                    else ""
                )
                investor_sentiment = (
                    data["impact_explanation"]["nature_of_impact"]["investor_sentiment"]
                    if data["impact_explanation"]["nature_of_impact"][
                        "investor_sentiment"
                    ]
                    else ""
                )
                market_volatility = (
                    data["impact_explanation"]["nature_of_impact"]["market_volatility"]
                    if data["impact_explanation"]["nature_of_impact"][
                        "market_volatility"
                    ]
                    else ""
                )
                Impact_detailed_explanation = (
                    data["impact_explanation"]["Impact_detailed_explanation"]
                    if data["impact_explanation"]["Impact_detailed_explanation"]
                    else ""
                )

                print("retries", retries)
                print("data scraperd")
                success = True

            except (json.JSONDecodeError, IndexError) as e:
                print(f"Failed to parse JSON: {e}. Retrying...")
                retries -= 1
                time.sleep(2)

        if not success:
            print("Failed to load and process JSON data after retries.")
            continue

        if "day ago" in time_to_out_news:
            ago_news = 24.0
        elif "hour" in time_to_out_news:
            if "hours" in time_to_out_news:
                ago_news = float(time_to_out_news.replace(" hours ago", ""))
            else:
                ago_news = float(time_to_out_news.replace(" hour ago", ""))

        elif "minute" in time_to_out_news:
            if "minutes" in time_to_out_news:
                ago_news = float(time_to_out_news.replace(" minutes ago", ""))
            else:
                ago_news = float(time_to_out_news.replace(" minute ago", ""))
        elif "second" in time_to_out_news:
            if "seconds" in time_to_out_news:
                ago_news = float(time_to_out_news.replace(" seconds ago", ""))
            else:
                ago_news = float(time_to_out_news.replace(" second ago", ""))

        updated_time = datetime.now() - timedelta(hours=ago_news)

        news_entry = NewsItem(
            title=title,
            published_date=published_date,
            summary=summary,
            classification=classification,
            type_of_impact=type_of_impact,
            description=impact_description,
            sectors=sectors_impacted,
            category=category_impacted,
            Country=Country,
            company_name=company_name,
            stock_name=stocks_impacted,
            scale_of_impact=scale_of_impact,
            timeframe_of_impact=timeframe_of_impact,
            investor_sentiment=investor_sentiment,
            market_volatility=market_volatility,
            detailed_explanation=Impact_detailed_explanation,
            time_to_out_news=time_to_out_news,
            feed=feed,
            other_news_link=link,
            similar=similar_news,
            created_at=updated_time,
            image=None
        )

        session.add(news_entry)
        session.commit()

        start_news += 1
        print(f"scraped number of news is {start_news}")

        # news_items.append(news_item)

    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "data": None,
            "error": None,
            "message": "News fetched successfully.",
        },
    )


# except HTTPException:
#     raise
# except Exception as e:
#     return JSONResponse(
#         status_code=500,
#         content={
#             "success": False,
#             "data": None,
#             "error": str(e),
#             "message": "Something went wrong!",
#         },
#     )


if __name__ == "__main__":
    globle_news()
