import json
import os
import regex as re
from fastapi import HTTPException
from fastapi.responses import JSONResponse
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from datetime import datetime, timedelta

from dotenv import load_dotenv

from server.utils.prompt import gemini_prompt
from server.db.base import SessionLocal
from server.models.news import NewsItem

load_dotenv()

gemini_ai_key = os.getenv("GEMINI_AI_KEY")
genai.configure(api_key=gemini_ai_key)

session = SessionLocal()

twenty_four_hours_ago = datetime.now() - timedelta(hours=24)


def cnbc_news():
    try:
        response = requests.get("https://www.cnbc.com/world/?region=world")
        html_content = response.content

        soup = BeautifulSoup(html_content, "html.parser")

        latest_news_section = soup.find(
            "div", class_="LatestNews-isHomePage LatestNews-isIntlHomepage"
        )

        if not latest_news_section:
            raise HTTPException(
                status_code=404,
                detail="No data found, Please try again after some time.",
            )

        start_news = 0
        for news_item in latest_news_section.select(".LatestNews-item"):
            timestamp = news_item.select_one(".LatestNews-timestamp").text.strip()
            news_link = news_item.select_one(".LatestNews-headline")["href"]
            headline = news_item.select_one(".LatestNews-headline").text.strip()

            article_response = requests.get(news_link)
            article_html = article_response.content
            article_soup = BeautifulSoup(article_html, "html.parser")

            key_points_section = article_soup.find(
                "div", class_="PageBuilder-col-9 PageBuilder-col PageBuilder-article"
            )
            key_points = (
                key_points_section.select(".RenderKeyPoints-list li")
                if key_points_section
                else []
            )

            key_points_result = (
                "\n".join(item.get_text(strip=True) for item in key_points)
                if key_points
                else ""
            )

            article_body_section = article_soup.find(
                "div", class_="ArticleBody-articleBody"
            )
            paragraphs = (
                article_body_section.select(".group p") if article_body_section else []
            )

            article_body_result = (
                "\n".join(item.get_text(strip=True) for item in paragraphs)
                if paragraphs
                else ""
            )

            news_data = {
                "headline": headline,
                "time_to_out_news": timestamp,
                "link": news_link,
                "key_points": key_points_result,
                "article_body": article_body_result,
            }
            existing_news = session.query(NewsItem).filter_by(title=headline).first()
            if existing_news:
                continue

            prompt = gemini_prompt(news_data)
            model = genai.GenerativeModel("gemini-1.5-flash")
            analysis = model.generate_content(prompt)
            print("data is provieded by Gemini AI")

            ai_data = analysis.text

            pattern = r"""\{(?:[^{}]|(?R))*\}"""
            matches = re.findall(pattern, ai_data, re.DOTALL)[0]
            breakpoint()

            data = json.loads(matches)
            title = data["article"]["title"] if data["article"]["title"] else ""
            published_date = (
                data["article"]["published_date"]
                if data["article"]["published_date"]
                else ""
            )
            summary = data["article"]["summary"] if data["article"]["summary"] else ""
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
                data["impact_analysis"]["majority_market_impact"]["impact_description"]
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
                if data["impact_explanation"]["nature_of_impact"]["investor_sentiment"]
                else ""
            )
            market_volatility = (
                data["impact_explanation"]["nature_of_impact"]["market_volatility"]
                if data["impact_explanation"]["nature_of_impact"]["market_volatility"]
                else ""
            )
            Impact_detailed_explanation = (
                data["impact_explanation"]["Impact_detailed_explanation"]
                if data["impact_explanation"]["Impact_detailed_explanation"]
                else ""
            )

            if "Hour" in timestamp:
                if "Hours" in timestamp:
                    ago_news = float(timestamp.replace(" Hours Ago", ""))
                else:
                    ago_news = float(timestamp.replace(" Hour Ago", ""))

            elif "Min" in timestamp:
                ago_news = float(timestamp.replace(" Min Ago", ""))
            elif "Second" in timestamp:
                if "Seconds" in timestamp:
                    ago_news = float(timestamp.replace(" Seconds Ago", ""))
                else:
                    ago_news = float(timestamp.replace(" Second Ago", ""))
            else:
                ago_news = 24.0

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
                time_to_out_news=ago_news,
                feed=None,
                other_news_link=news_link,
                similar=None,
                created_at=updated_time,
            )
            session.add(news_entry)
            session.commit()

            start_news += 1
            print(f"scraped number of news is {start_news}")

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
    cnbc_news()
