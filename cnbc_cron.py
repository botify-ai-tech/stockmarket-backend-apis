import json
import os
import random
import time
import unicodedata
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

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait

load_dotenv()

gemini_ai_key = os.getenv("GEMINI_AI_KEY")
genai.configure(api_key=gemini_ai_key)

session = SessionLocal()

twenty_four_hours_ago = datetime.now() - timedelta(hours=24)


def normalize_title(title):
    title = unicodedata.normalize("NFKD", title)
    title = title.encode("ascii", "ignore").decode("utf-8")
    title = title.lower()
    title = re.sub(r"\s+", "", title)            
    title = re.sub(r"[^\w]", "", title)          
    return title

def is_duplicate_title(title):
    normalized = normalize_title(title)

    recent_news = session.query(NewsItem).order_by(NewsItem.created_at.desc()).limit(100).all()

    for news in recent_news:
        if normalize_title(news.title) == normalized:
            return True

    return False

# def get_cnbc_soup():
#     chrome_options = Options()
#     chrome_options.add_argument("--headless")
#     chrome_options.add_argument("--disable-gpu") 
#     chrome_options.add_argument("--no-sandbox")
#     chrome_options.add_argument("--disable-dev-shm-usage")
#     chrome_options.add_argument("--disable-blink-features=AutomationControlled")
#     chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36")

#     driver = webdriver.Chrome(options=chrome_options)
#     try:
#         driver.get("https://www.cnbc.com/world/?region=world")
#         time.sleep(random.randint(5, 10))  # Let the JS render content
#         html = driver.page_source

#         return BeautifulSoup(html, "html.parser")
#     finally:
#         driver.quit()


# def get_cnbc_latest_news_section(scrolls=10, wait_time=2):
#     options = Options()
#     options.add_argument("--headless")  # comment this if you want to watch it scroll
#     options.add_argument("--disable-gpu")
#     options.add_argument("--no-sandbox")

#     driver = webdriver.Chrome(options=options)
#     driver.get("https://www.cnbc.com/world/?region=world")
#     time.sleep(5)  # let the page load

#     # Find the Latest News container
#     try:
#         latest_news_section = driver.find_element(By.CLASS_NAME, "LatestNews-container")
#     except:
#         driver.quit()
#         raise Exception("Could not find the Latest News section")

#     for _ in range(scrolls):
#         driver.execute_script(
#             "arguments[0].scrollTop = arguments[0].scrollHeight", latest_news_section
#         )
#         time.sleep(wait_time)

#     html = latest_news_section.get_attribute("outerHTML")
#     driver.quit()

#     return BeautifulSoup(html, "html.parser")


# def cnbc_news():

#     try:
        
#         # soup = get_cnbc_soup()
#         soup = get_cnbc_latest_news_section(scrolls=15)

#         latest_news_section = soup.find(
#             "div", class_="LatestNews-isHomePage LatestNews-isIntlHomepage"
#         )
#         time.sleep(random.randint(1, 10))


#         if not latest_news_section:
#             raise HTTPException(
#                 status_code=404,
#                 detail="No data found, Please try again after some time.",
#             )

#         start_news = 0
#         for news_item in latest_news_section.select(".LatestNews-item"):
#             time.sleep(random.randint(1, 10))

#             timestamp = news_item.select_one(".LatestNews-timestamp").text.strip()
#             news_link = news_item.select_one(".LatestNews-headline")["href"]
#             headline = news_item.select_one(".LatestNews-headline").text.strip()

#             article_response = requests.get(news_link)

#             article_html = article_response.content
#             article_soup = BeautifulSoup(article_html, "html.parser")

#             pro_news = article_soup.find("div", class_="background ng-scope")
#             if pro_news:
#                 print("This new conn't be scraped due to security.")
#                 continue

#             key_points_section = article_soup.find(
#                 "div", class_="PageBuilder-col-9 PageBuilder-col PageBuilder-article"
#             )
#             key_points = (
#                 key_points_section.select(".RenderKeyPoints-list li")
#                 if key_points_section
#                 else []
#             )

#             key_points_result = (
#                 "\n".join(item.get_text(strip=True) for item in key_points)
#                 if key_points
#                 else ""
#             )

#             article_body_section = article_soup.find(
#                 "div", class_="ArticleBody-articleBody"
#             )
#             paragraphs = (
#                 article_body_section.select(".group p") if article_body_section else []
#             )

#             article_body_result = (
#                 "\n".join(item.get_text(strip=True) for item in paragraphs)
#                 if paragraphs
#                 else ""
#             )

#             img_tag = article_soup.select_one("picture[data-test='Picture'] img[src]")
#             image = img_tag["src"] if img_tag else None

#             news_data = {
#                 "headline": headline,
#                 "time_to_out_news": timestamp,
#                 "link": news_link,
#                 "key_points": key_points_result,
#                 "article_body": article_body_result,
#                 "image": image,
#             }

#             if is_duplicate_title(headline):
#                 print("----------------------")
#                 print("Duplicate")
#                 continue

#             retries = 3  # Retry up to 3 times
#             success = False

#             while retries > 0 and not success:
#                 try:
#                     time.sleep(random.randint(1, 20))


#                     prompt = gemini_prompt(news_item)
#                     model = genai.GenerativeModel("gemini-1.5-flash")
#                     analysis = model.generate_content(prompt)
#                     print("data is provieded by Gemini AI")

#                     ai_data = analysis.text
#                     pattern = r"""\{(?:[^{}]|(?R))*\}"""

#                     matches = re.findall(pattern, ai_data, re.DOTALL)[0]
#                     data = json.loads(matches)

#                     title = data["article"]["title"] if data["article"]["title"] else ""
#                     published_date = (
#                         data["article"]["published_date"]
#                         if data["article"]["published_date"]
#                         else ""
#                     )
#                     summary = (
#                         data["article"]["summary"] if data["article"]["summary"] else ""
#                     )
#                     classification = (
#                         data["classification"]["primary_class"]
#                         if data["classification"]["primary_class"]
#                         else ""
#                     )
#                     type_of_impact = (
#                         data["impact_analysis"]["type_of_impact"]
#                         if data["impact_analysis"]["type_of_impact"]
#                         else ""
#                     )
#                     impact_description = (
#                         data["impact_analysis"]["majority_market_impact"][
#                             "impact_description"
#                         ]
#                         if data["impact_analysis"]["majority_market_impact"][
#                             "impact_description"
#                         ]
#                         else ""
#                     )
#                     sectors_impacted = (
#                         data["impact_analysis"]["sectors_impacted"]["sector_list"]
#                         if data["impact_analysis"]["sectors_impacted"]["sector_list"]
#                         else ""
#                     )
#                     category_impacted = (
#                         data["category_impacted"]["category_list"]
#                         if data["category_impacted"]["category_list"]
#                         else ""
#                     )
#                     Country = (
#                         data["Country"]["country_name"]
#                         if data["Country"]["country_name"]
#                         else ""
#                     )
#                     company_name = (
#                         data["company_name"]["company_name"]
#                         if data["company_name"]["company_name"]
#                         else ""
#                     )
#                     stocks_impacted = (
#                         data["impact_analysis"]["stocks_impacted"]["stock_list"]
#                         if data["impact_analysis"]["stocks_impacted"]["stock_list"]
#                         else ""
#                     )
#                     scale_of_impact = (
#                         data["impact_explanation"]["scale_of_impact"]
#                         if data["impact_explanation"]["scale_of_impact"]
#                         else ""
#                     )
#                     timeframe_of_impact = (
#                         data["impact_explanation"]["timeframe_of_impact"]
#                         if data["impact_explanation"]["timeframe_of_impact"]
#                         else ""
#                     )
#                     investor_sentiment = (
#                         data["impact_explanation"]["nature_of_impact"]["investor_sentiment"]
#                         if data["impact_explanation"]["nature_of_impact"][
#                             "investor_sentiment"
#                         ]
#                         else ""
#                     )
#                     market_volatility = (
#                         data["impact_explanation"]["nature_of_impact"]["market_volatility"]
#                         if data["impact_explanation"]["nature_of_impact"][
#                             "market_volatility"
#                         ]
#                         else ""
#                     )
#                     Impact_detailed_explanation = (
#                         data["impact_explanation"]["Impact_detailed_explanation"]
#                         if data["impact_explanation"]["Impact_detailed_explanation"]
#                         else ""
#                     )

#                     print("retries", retries)
#                     print("data scraperd")
#                     success = True

#                 except (json.JSONDecodeError, IndexError) as e:
#                     print(f"Failed to parse JSON: {e}. Retrying...")
#                     retries -= 1
#                     time.sleep(2)

#             if not success:
#                 print("Failed to load and process JSON data after retries.")
#                 continue

#             if "Hour" in timestamp:
#                 if "Hours" in timestamp:
#                     ago_news = float(timestamp.replace(" Hours Ago", ""))
#                 else:
#                     ago_news = float(timestamp.replace(" Hour Ago", ""))

#             elif "Min" in timestamp:
#                 minutes = float(timestamp.replace(" Min Ago", ""))
#                 ago_news = minutes / 60
#             elif "Second" in timestamp:
#                 if "Seconds" in timestamp:
#                     seconds = float(timestamp.replace(" Seconds Ago", ""))
#                     ago_news = seconds / 3600
#                 else:
#                     seconds = float(timestamp.replace(" Second Ago", ""))
#                     ago_news = seconds / 3600
#             else:
#                 ago_news = 24.0

#             updated_time = datetime.now() - timedelta(hours=ago_news)
#             print(title)
#             print(updated_time)
#             # news_entry = NewsItem(
#             #     title=title,
#             #     published_date=published_date,
#             #     summary=summary,
#             #     classification=classification,
#             #     type_of_impact=type_of_impact,
#             #     description=impact_description,
#             #     sectors=sectors_impacted,
#             #     category=category_impacted,
#             #     Country=Country,
#             #     company_name=company_name,
#             #     stock_name=stocks_impacted,
#             #     scale_of_impact=scale_of_impact,
#             #     timeframe_of_impact=timeframe_of_impact,
#             #     investor_sentiment=investor_sentiment,
#             #     market_volatility=market_volatility,
#             #     detailed_explanation=Impact_detailed_explanation,
#             #     time_to_out_news=ago_news,
#             #     feed=None,
#             #     other_news_link=news_link,
#             #     similar=None,
#             #     created_at=updated_time,
#             #     image=image
#             # )
#             # session.add(news_entry)
#             # session.commit()

#             start_news += 1
#             print(f"scraped number of news is {start_news}")

#         return JSONResponse(
#             status_code=200,
#             content={
#                 "success": True,
#                 "data": None,
#                 "error": None,
#                 "message": "News fetched successfully.",
#             },
#         )


#     except HTTPException as e:
#         return JSONResponse(
#             status_code=e.status_code,
#             content={
#                 "success": False,
#                 "data": None,
#                 "error": str(e.detail),
#                 "message": "Data not found error",
#             },
#         )

#     except Exception as e:
#         return JSONResponse(
#             status_code=500,
#             content={
#                 "success": False,
#                 "data": None,
#                 "error": str(e),
#                 "message": "Something went wrong!",
#             },
#         )


# if __name__ == "__main__":
#     res = cnbc_news()
#     print(res.status_code)
#     print(res.body.decode()) 



from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import random
import json
import re
import requests
from datetime import datetime, timedelta
from fastapi import HTTPException
from fastapi.responses import JSONResponse
import google.generativeai as genai


def get_cnbc_latest_news_section(scrolls=15, wait_time=2):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(options=options)
    driver.get("https://www.cnbc.com/world/?region=world")
    time.sleep(5)

    try:
        latest_news_section = driver.find_element(By.CLASS_NAME, "LatestNews-container")
    except:
        driver.quit()
        raise Exception("Could not find the Latest News section")

    for _ in range(scrolls):
        driver.execute_script(
            "arguments[0].scrollTop = arguments[0].scrollHeight", latest_news_section
        )
        time.sleep(wait_time)

    html = latest_news_section.get_attribute("outerHTML")
    driver.quit()

    return BeautifulSoup(html, "html.parser")


def cnbc_news():
    try:
        soup = get_cnbc_latest_news_section(scrolls=15)
        latest_news_section = soup.find("div", class_="LatestNews-isHomePage LatestNews-isIntlHomepage")
        time.sleep(random.randint(1, 5))

        if not latest_news_section:
            raise HTTPException(status_code=404, detail="No data found, Please try again after some time.")

        start_news = 0
        for news_item in latest_news_section.select(".LatestNews-item"):
            time.sleep(random.randint(1, 5))

            try:
                timestamp = news_item.select_one(".LatestNews-timestamp").text.strip()
                news_link = news_item.select_one(".LatestNews-headline")["href"]
                headline = news_item.select_one(".LatestNews-headline").text.strip()
            except:
                continue

            article_response = requests.get(news_link)
            article_html = article_response.content
            article_soup = BeautifulSoup(article_html, "html.parser")

            pro_news = article_soup.find("div", class_="background ng-scope")
            if pro_news:
                continue

            key_points_section = article_soup.find("div", class_="PageBuilder-col-9 PageBuilder-col PageBuilder-article")
            key_points = key_points_section.select(".RenderKeyPoints-list li") if key_points_section else []
            key_points_result = "\n".join(item.get_text(strip=True) for item in key_points) if key_points else ""

            article_body_section = article_soup.find("div", class_="ArticleBody-articleBody")
            paragraphs = article_body_section.select(".group p") if article_body_section else []
            article_body_result = "\n".join(item.get_text(strip=True) for item in paragraphs) if paragraphs else ""

            img_tag = article_soup.select_one("picture[data-test='Picture'] img[src]")
            image = img_tag["src"] if img_tag else None

            if is_duplicate_title(headline):
                continue

            retries = 3
            success = False
            while retries > 0 and not success:
                try:
                    time.sleep(random.randint(1, 10))

                    prompt = gemini_prompt(news_item)
                    model = genai.GenerativeModel("gemini-1.5-flash")
                    analysis = model.generate_content(prompt)

                    ai_data = analysis.text
                    pattern = r"\{(?:[^{}]|(?R))*\}"
                    matches = re.findall(pattern, ai_data, re.DOTALL)[0]
                    data = json.loads(matches)

                    title = data["article"].get("title", "")
                    published_date = data["article"].get("published_date", "")
                    summary = data["article"].get("summary", "")
                    classification = data["classification"].get("primary_class", "")
                    type_of_impact = data["impact_analysis"].get("type_of_impact", "")
                    impact_description = data["impact_analysis"].get("majority_market_impact", {}).get("impact_description", "")
                    sectors_impacted = data["impact_analysis"].get("sectors_impacted", {}).get("sector_list", "")
                    category_impacted = data["category_impacted"].get("category_list", "")
                    Country = data["Country"].get("country_name", "")
                    company_name = data["company_name"].get("company_name", "")
                    stocks_impacted = data["impact_analysis"].get("stocks_impacted", {}).get("stock_list", "")
                    scale_of_impact = data["impact_explanation"].get("scale_of_impact", "")
                    timeframe_of_impact = data["impact_explanation"].get("timeframe_of_impact", "")
                    investor_sentiment = data["impact_explanation"].get("nature_of_impact", {}).get("investor_sentiment", "")
                    market_volatility = data["impact_explanation"].get("nature_of_impact", {}).get("market_volatility", "")
                    Impact_detailed_explanation = data["impact_explanation"].get("Impact_detailed_explanation", "")

                    success = True

                except (json.JSONDecodeError, IndexError) as e:
                    retries -= 1
                    time.sleep(2)

            if not success:
                continue

            ago_news = 24.0
            if "Hour" in timestamp:
                ago_news = float(timestamp.split()[0])
            elif "Min" in timestamp:
                ago_news = float(timestamp.split()[0]) / 60
            elif "Second" in timestamp:
                ago_news = float(timestamp.split()[0]) / 3600

            updated_time = datetime.now() - timedelta(hours=ago_news)
            print(title)
            print(updated_time)
            print(f"scraped number of news is {start_news + 1}")

            start_news += 1

        return JSONResponse(
            status_code=200,
            content={"success": True, "data": None, "error": None, "message": "News fetched successfully."},
        )

    except HTTPException as e:
        return JSONResponse(
            status_code=e.status_code,
            content={"success": False, "data": None, "error": str(e.detail), "message": "Data not found error"},
        )

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "data": None, "error": str(e), "message": "Something went wrong!"},
        )


if __name__ == "__main__":
    res = cnbc_news()
    print(res.status_code)
    print(res.body.decode())
