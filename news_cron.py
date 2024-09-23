import json
import os
import re
import time
from dotenv import load_dotenv
from datetime import datetime, timedelta

from bs4 import BeautifulSoup
import requests

from fastapi.responses import JSONResponse
from fastapi import HTTPException

from server.db.base import Session
from server.models.news import StockNews

import google.generativeai as genai

load_dotenv()

gemini_ai_key = os.getenv("GEMINI_AI_KEY")
genai.configure(api_key=gemini_ai_key)

session = Session()

twenty_four_hours_ago = datetime.now() - timedelta(hours=24)


def globle_news():
    try:
        response = requests.get("https://pulse.zerodha.com/")
        if response.status_code != 200:
            raise Exception(
                "Failed to load page. Status code: {}".format(response.status_code)
            )

        soup = BeautifulSoup(response.content, "html.parser")

        html_contents = soup.find_all("li", class_="box item")

        if not html_contents:
            raise Exception("No results found, Please try again after some time.")

        # news_items = []
        start_news = 0
        for item in html_contents:

            title = item.find("h2", class_="title").get_text(strip=True)
            description = item.find("div", class_="desc").get_text(strip=True)
            time_to_out_news = item.find("span", class_="date").get_text(strip=True)
            feed = (
                item.find("span", class_="feed").get_text(strip=True).replace("— ", "")
            )
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
            existing_news = session.query(StockNews).filter_by(title=title).first()
            if existing_news:
                continue
            time.sleep(4)
            model = genai.GenerativeModel("gemini-1.5-flash")
            analysis = model.generate_content(
                f"""Task: Analyze the provided JSON news data and extract the following information:\nCompany Name: Identify the primary company or organization that is the central focus of the news. [Technology, Healthcare, Financials, Consumer Discretionary, Consumer Staples, Energy, Utilities, Materials, Industrials, Real Estate, Telecommunications] these are sectors pick Sectors Involved from this list. \nStock Name: Provide the corresponding stock ticker symbol for the company, ensuring it is listed on either the National Stock Exchange (NSE) or the Bombay Stock Exchange (BSE).\nSectors Involved: Determine the relevant industry sectors that are directly impacted or mentioned in the news.\nCategory of News: Classify the news based on its content into one or more categories (e.g., Market Movement, Macroeconomic Factors, Mergers and Acquisitions, Regulatory/Policy Updates, Financial Performance, Product Launches).\nInstructions:\nPrioritize Central Company: If multiple companies are mentioned, prioritize the one that is most central to the news content.\nIdentify Relevant Sectors: Include only sectors that are directly affected or discussed in the news.\nAccurate Categorization: Choose the most fitting category based on the primary content of the news.\nConsider Contextual Factors: When predicting stock movement, consider factors such as market trends, industry-specific news, and the overall sentiment of the news.\nAdhere to Format: Strictly follow the specified JSON format and do not include any additional information beyond what is requested.\nFormat:\n\n{{  "Company Name": "Name of the company",  "Stock Name": "Stock ticker symbol (NSE or BSE)",  "Sectors Involved": ["Sector 1", "Sector 2", ...],  "Category of News": "News category"}}\n\n\nAdditional Considerations:\nData Quality: Ensure that the JSON data is clean, accurate, and relevant to the news analysis.\nStrict Note:\nDo not provide any additional information or explanation in the response.\n input data: {news_item}"""
            )
            print("data is provieded by Gemini AI")

            ai_data = analysis.text
            pattern = r"\{.*?\}"

            matches = re.findall(pattern, ai_data, re.DOTALL)[0]

            data = json.loads(matches)
            company_name = data["Company Name"] if data["Company Name"] else ""
            stock_name = data["Stock Name"] if data["Stock Name"] else ""
            sectors = data["Sectors Involved"] if data["Sectors Involved"] else []
            category = data["Category of News"] if data["Category of News"] else ""

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

            news_entry = StockNews(
                title=title,
                description=description,
                time_to_out_news=time_to_out_news,
                feed=feed,
                link=link,
                similar=similar_news,
                created_at=updated_time,
                company_name=company_name,
                stock_name=stock_name,
                sectors=sectors,
                category=category,
            )
            session.merge(news_entry)
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


if __name__ == "__main__":
    globle_news()
