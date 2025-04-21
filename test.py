# import logging
# import time
# from bs4 import BeautifulSoup
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.options import Options
# from selenium.common.exceptions import NoSuchElementException, WebDriverException

# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s - %(levelname)s - %(message)s",
# )

# def scrap_daily1(share):
#     all_screener_data_dict = {}

#     try:
#         logging.info("Starting Ticker scraping")

#         # Set Chrome options for headless scraping
#         chrome_options = Options()
#         chrome_options.add_argument("--headless")
#         chrome_options.add_argument("--disable-gpu")
#         chrome_options.add_argument("--window-size=1920,1080")
#         chrome_options.add_argument("--no-sandbox")
#         chrome_options.add_argument("--disable-dev-shm-usage")

#         driver = webdriver.Chrome(options=chrome_options)
#         driver.get(f"https://ticker.finology.in/company/{share}")
#         time.sleep(2)

#         company_essentials_html = driver.find_element(
#             By.XPATH,
#             "//div[@id='mainContent_divCompanyEssentials']//div[@id='mainContent_updAddRatios']",
#         ).get_attribute("outerHTML")
#         driver.quit()

#         soup = BeautifulSoup(company_essentials_html, "html.parser")
#         data = {}
#         divs = soup.find_all("div", class_="col-6 col-md-4 compess")

#         for div in divs:
#             label = div.find("small")
#             label_text = label.get_text(strip=True) if label else ""
#             number_span = div.find("span", class_="Number")
#             number_p = div.find("p")
#             number_value = (
#                 number_span.get_text(strip=True) if number_span
#                 else number_p.get_text(strip=True) if number_p
#                 else "0"
#             )
#             if label_text:
#                 data[label_text] = number_value

#         all_screener_data_dict[share] = {
#             "Ticker": {
#                 "Company Essentials": [data]
#             }
#         }

#         essentials = all_screener_data_dict[share]["Ticker"]["Company Essentials"][0]
#         print(f"\n📊 Company Overview: {share}")
#         print(f"Market Cap        : {essentials.get('Market Cap')}")
#         print(f"Enterprise Value  : {essentials.get('Enterprise Value')}")
#         print(f"P/B Ratio         : {essentials.get('P/B')}")
#         print(f"P/E Ratio         : {essentials.get('P/E')}")
#         print(f"Total Debt        : {essentials.get('DEBT')}")
#         print(f"Dividend Yield    : {essentials.get('Div. Yield')}")

#     except NoSuchElementException:
#         logging.error(f"Failed to find elements for {share}")
#         return {"share": share, "status": "Failed"}

#     except WebDriverException as e:
#         logging.error(f"[{share}] WebDriver error: {str(e)}")
#         return {"share": share, "status": "Failed", "error": str(e)}

#     except Exception as e:
#         logging.error(f"Error scraping {share}: {str(e)}")
#         return {"share": share, "status": "Error", "error": str(e)}


# if __name__ == "__main__":
#     scrap_daily1("A2ZINFRA")


# def get_new_search_query(
    #     self, db: Session, search: str, skip: int = 0, limit: int = 10
    # ) -> NewsItem:
    #     return (
    #         db.query(NewsItem)
    #         .filter(
    #             and_(
    #                 NewsItem.created_at >= last_24_hours,
    #                 or_(
    #                     NewsItem.company_name.ilike(f"%{search}%"),
    #                     NewsItem.sectors.any(search),
    #                 ),
    #             )
    #         )
    #         .order_by(NewsItem.created_at.desc())
    #         .offset(skip)
    #         .limit(limit)
    #         .all()
    #     )

    # def get_total_new_search_query(
    #     self,
    #     db: Session,
    #     search: str,
    # ) -> NewsItem:
    #     return (
    #         db.query(NewsItem)
    #         .filter(
    #             and_(
    #                 NewsItem.created_at >= last_24_hours,
    #                 or_(
    #                     NewsItem.company_name.ilike(f"%{search}%"),
    #                     NewsItem.sectors.any(search),
    #                 ),
    #             )
    #         )
    #         .count()
    #     )

    # def get_new_without_search_query(
    #     self, db: Session, skip: int = 0, limit: int = 10
    # ) -> NewsItem:
    #     return (
    #         db.query(NewsItem)
    #         .filter(NewsItem.created_at >= last_24_hours)
    #         .order_by(NewsItem.created_at.desc())
    #         .offset(skip)
    #         .limit(limit)
    #         .all()
    #     )

    # def get_last_48_hours_news(
    #     self, db: Session, skip: int = 0, limit: int = 10
    # ) -> NewsItem:
    #     return (
    #         db.query(NewsItem)
    #         .filter(NewsItem.created_at >= cutoff_time)
    #         .order_by(NewsItem.created_at.desc())
    #         .offset(skip)
    #         .limit(limit)
    #         .all()
    #     )
    
    # def get_total_news_without_search_query(self, db: Session) -> NewsItem:
    #     return db.query(NewsItem).filter(NewsItem.created_at >= last_24_hours).count()









# from concurrent.futures import ThreadPoolExecutor, as_completed
# from datetime import datetime
# from io import StringIO 
# from server.db.base import SessionLocal
# from dotenv import load_dotenv
# import logging
# import time
# from bs4 import BeautifulSoup
# import random
# import pandas as pd
# import requests
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.support.wait import WebDriverWait
# from server.models.ratio import CalculateRatio, Company
# from sqlalchemy.exc import SQLAlchemyError
# from selenium.common.exceptions import NoSuchElementException, WebDriverException

# load_dotenv()

# logging.basicConfig(
#     level=logging.INFO,  
#     format="%(asctime)s - %(levelname)s - %(message)s",  
# )

# with open("ratio\\nsc.txt", "r", encoding="utf-8") as f:
#     all_shares = [line.strip() for line in f.readlines()]

# # number of parallel threads
# NUM_THREADS = 2
# MAX_RETRIES = 3
# RETRY_DELAY = 5

# def scrap_daily(share):
#     session = SessionLocal()
#     all_screener_data_dict = {}
#     try :

#         # Initialize the WebDriver with options
#         driver = webdriver.Chrome()

#         driver.maximize_window()
#         driver.get("https://www.screener.in/")

#         # login
#         driver.refresh()
#         time.sleep(random.randint(1, 10))

#         driver.find_element(By.XPATH, "//a[@class='button account']").click()
#         email = driver.find_element(By.XPATH, "//input[@id='id_username']")
#         email.clear()
#         email.send_keys("het331.rejoice@gmail.com")

#         password = driver.find_element(By.XPATH, "//input[@id='id_password']")
#         password.clear()
#         password.send_keys("Het@9676")

#         driver.find_element(By.XPATH, "//button[@class='button-primary']").click()
#         logging.info("Login")

#         try:
#             driver.refresh()
#             time.sleep(random.randint(1, 10))
#             driver.refresh()
#             search = driver.find_element(
#                 By.XPATH, "//div[@class='search']//input[@class='u-full-width']"
#             )
#             search.clear()
#             search.send_keys(share)
#             time.sleep(random.randint(1, 10))
#             search.send_keys(" ")
#             time.sleep(1)
#             # search.send_keys(Keys.DOWN)
#             search.send_keys(Keys.ENTER)
#         except:
#             pass

#         share_name = driver.find_element(
#             By.XPATH,
#             "//div[@class='card card-large']//div[@class='flex-row flex-wrap flex-align-center flex-grow']//h1[@class='margin-0 show-from-tablet-landscape']",
#         ).text
#         logging.info(share_name)

#         share_price = driver.find_element(
#             By.XPATH,
#             "//div[@class='card card-large']//div//div//div[@class='flex flex-align-center']",
#         ).text.split("\n")[0]

#         # Share Price percentage
#         try:
#             share_price_percentage = driver.find_element(
#                 By.XPATH,
#                 "//span[@class='font-size-12 down margin-left-4']",
#             ).text
#         except:
#             try:
#                 share_price_percentage = driver.find_element(
#                     By.XPATH,
#                     "//span[@class='font-size-12 up margin-left-4']",
#                 ).text
#             except:
#                 share_price_percentage = "0.0%"

#         all_screener_data_dict[share_name] = {}
#         all_screener_data_dict[share_name]["Screener"] = {}
#         all_screener_data_dict[share_name]["Ticker"] = {}

#         all_screener_data_dict[share_name]["Screener"] = {
#             "share_name": share_name,
#             "share_price": share_price,
#             "share_price_percentage": share_price_percentage,
#         }


#         # ------------------------------------------------------------ Peer comparison ------------------------------------------------------------
#         logging.info("Peer comparison")

#         peer_table_data = []
#         for peer_table_index in driver.find_elements(
#             By.XPATH,
#             "//section[@id='peers']//div//div[@class='responsive-holder fill-card-width']//table//tbody//tr",
#         ):
#             row_data = [
#                 th.text for th in peer_table_index.find_elements(By.TAG_NAME, "th")
#             ]
#             if row_data == [] or row_data == [""]:
#                 continue
#             peer_table_data.append(row_data)

#         for peer_table_value in driver.find_elements(
#             By.XPATH,
#             "//section[@id='peers']//div//div[@class='responsive-holder fill-card-width']//table//tbody//tr",
#         ):
#             row_data = [
#                 td.text for td in peer_table_value.find_elements(By.TAG_NAME, "td")
#             ]
#             if row_data == [] or row_data == [""]:
#                 continue
#             peer_table_data.append(row_data)

#         # for peer_table_value in driver.find_elements(
#         #     By.XPATH,
#         #     "//section[@id='peers']//div//div[@class='responsive-holder fill-card-width']//table//tfoot//tr",
#         # ):
#         #     row_data = [
#         #         td.text for td in peer_table_value.find_elements(By.TAG_NAME, "td")
#         #     ]
#         #     if row_data == [] or row_data == [""]:
#         #         continue
#         #     # peer_table_data.append(row_data)

#         headers = peer_table_data[0]

#         # Convert list of lists to list of dictionaries
#         json_data = [dict(zip(headers, row)) for row in peer_table_data[1:]]

#         # -------------------------------------------- Average P/E ---------------------------------------------------------------------

#         total_pe = 0
#         count = 0

#         for peer_detail in json_data:
#             pe_value = peer_detail.get("P/E")
#             if pe_value:
#                 total_pe += float(pe_value)
#                 count += 1

#         average_pe = round(total_pe / count, 2) if count > 0 else 0

#         all_screener_data_dict[share_name]["Screener"]["Average P/E"] = average_pe


#         # ------------------------------------------Sector and industry P/E------------------------------------------------------------------
#         sectore_link = driver.find_element(By.XPATH, "//section[@id='peers']//div[@class='flex flex-space-between']//p//a[1][@href]").get_attribute("href")
#         industry_link = driver.find_element(By.XPATH, "//section[@id='peers']//div[@class='flex flex-space-between']//p//a[2][@href]").get_attribute("href")
#         time.sleep(3)
#         driver.get(sectore_link)
#         try:
#             page_numbers = driver.find_elements(By.XPATH, "//div[@class='pagination']//div[@class='flex-baseline options']//a")
#             if page_numbers:
#                 page_number = max([int(max_page_number.text.replace("Next", "0")) for max_page_number in page_numbers])
#             else:
#                 page_number = 1
#             print("Total Page Number Industry PE... ", page_number)

#             total_data = []
#             for i in range(1, page_number+1):
#                 url = f"{sectore_link}?page={i}"
#                 res = requests.get(url, headers={"user-agent" : "Custom Agent"})
#                 time.sleep(0.5)
#                 extracted_tables = pd.read_html(StringIO(res.text))
#                 extracted_tables = extracted_tables[0][extracted_tables[0]['S.No.'] != "S.No."]
#                 total_data.append(extracted_tables)
#             df = pd.concat(total_data)
#             df['P/E'] =  pd.to_numeric( df['P/E']) 
#             sectore_pe = round(df['P/E'].mean(), 2)
#         except:
#             res = requests.get(sectore_link, headers={"user-agent" : "Custom Agent"})
#             extracted_tables = pd.read_html(StringIO(res.text))
#             extracted_tables = extracted_tables[0][extracted_tables[0]['S.No.'] != "S.No."]
#             df = pd.concat([extracted_tables])
#             df['P/E'] =  pd.to_numeric(df['P/E']) 
#             sectore_pe = round(df['P/E'].mean(), 2)
        
        
#         driver.get(industry_link)
#         try:
#             page_numbers = driver.find_elements(By.XPATH, "//div[@class='pagination']//div[@class='flex-baseline options']//a")
#             if page_numbers:
#                 page_number = max([int(max_page_number.text.replace("Next", "0")) for max_page_number in page_numbers])
#             else:
#                 page_number = 1
#             print("Total Page Number Industry PE... ", page_number)

#             total_data = []

#             for i in range(1, page_number+1):
#                 url = f"{sectore_link}?page={i}"
#                 res = requests.get(url, headers={"user-agent" : "Custom Agent"})
#                 time.sleep(0.5)
#                 extracted_tables = pd.read_html(StringIO(res.text))
#                 extracted_tables = extracted_tables[0][extracted_tables[0]['S.No.'] != "S.No."]
#                 total_data.append(extracted_tables)

#             df = pd.concat(total_data)
#             df['P/E'] =  pd.to_numeric( df['P/E']) 
#             industry_pe = round(df['P/E'].mean(), 2)    
#         except Exception as e:
#             res = requests.get(industry_link, headers={"user-agent" : "Custom Agent"})
#             time.sleep(3)
#             extracted_tables = pd.read_html(StringIO(res.text))
#             extracted_tables = extracted_tables[0][extracted_tables[0]['S.No.'] != "S.No."]
#             df = pd.concat([extracted_tables])
#             df['P/E'] =  pd.to_numeric(df['P/E']) 
#             industry_pe = round(df['P/E'].mean(), 2)

#         driver.quit()


#         # ----------------------------------------------------------------Ticker-----------------------------------------------------------------------------------
#         logging.info("Ticker")
#         chrome_options = Options()
#         chrome_options.add_argument("--headless")
#         chrome_options.add_argument("--disable-gpu")
#         chrome_options.add_argument("--window-size=1920,1080")
#         chrome_options.add_argument("--no-sandbox")
#         chrome_options.add_argument("--disable-dev-shm-usage")

#         # Initialize the WebDriver with options
#         driver = webdriver.Chrome(options=chrome_options)

#         time.sleep(2)
#         # driver = webdriver.Chrome()
#         driver.maximize_window()
#         driver.get(f"https://ticker.finology.in/company/{share}")

#         time.sleep(1)
#         company_essentials = driver.find_element(
#             By.XPATH,
#             "//div[@id='mainContent_divCompanyEssentials']//div[@id='mainContent_updAddRatios']",
#         ).get_attribute("outerHTML")

#         soup = BeautifulSoup(company_essentials, "html.parser")

#         data = {}
#         company_essentials_detail = []
#         # Extract all divs with class 'col-6 col-md-4 compess'
#         divs = soup.find_all("div", class_="col-6 col-md-4 compess")

#         for div in divs:
#             # Extract the label (small text)
#             label = div.find("small")
#             if label:
#                 label_text = label.get_text(strip=True)
#             # Extract the number value (which is inside a span with class 'Number')
#             number_span = div.find("span", class_="Number")
#             number_p = div.find("p")

#             if number_span:
#                 number_value = number_span.get_text(strip=True)
#             elif number_p:
#                 number_value = number_p.get_text(strip=True)
#             else:
#                 number_value = "0"
#             # Add the extracted data to the dictionary
#             if label_text and number_value:
#                 data[label_text] = number_value

#         company_essentials_detail.append(data)

#         all_screener_data_dict[share_name]["Ticker"][
#             "Company Essentials"
#         ] = company_essentials_detail
#         driver.quit()

#         time.sleep(3)


#     # -----------------------------------------------------------------------------------------------------------------------------------------------

#         market_cap = all_screener_data_dict[share_name]["Ticker"]["Company Essentials"][0].get("Market Cap")
#         enterprise_value = all_screener_data_dict[share_name]["Ticker"]["Company Essentials"][0].get("Enterprise Value")
#         pb_ratio = all_screener_data_dict[share_name]["Ticker"]["Company Essentials"][0].get("P/B")
#         pe_ratio = all_screener_data_dict[share_name]["Ticker"]["Company Essentials"][0].get("P/E")
#         debt = all_screener_data_dict[share_name]["Ticker"]["Company Essentials"][0].get("DEBT")
#         dividend_yield = all_screener_data_dict[share_name]["Ticker"]["Company Essentials"][0].get("Div. Yield")
#         time.sleep(3)

#         exitst_data = (
#             session.query(Company).filter(Company.share_symbol == share).first()
#         )
#         if exitst_data:
#             exitst_data.share_price = share_price
#             exitst_data.average_pe = average_pe
#             exitst_data.share_price_percentage = share_price_percentage
#             exitst_data.market_cap = market_cap
#             exitst_data.pb_ratio = pb_ratio
#             exitst_data.enterprise_value = enterprise_value
#             exitst_data.pe_ratio = pe_ratio
#             exitst_data.dividend_yield = dividend_yield
#             exitst_data.debt = debt
#             exitst_data.industry_pe = industry_pe
#             exitst_data.sectore_pe = sectore_pe
#             session.commit()

#             logging.info(f" {share} Data Updated.")
#         else : 
#             logging.info(f"{share} Company Not Exist.")

#         return {"share": share, "status": "Success"}

#     except NoSuchElementException:
#         logging.error(f"Failed to find elements for {share}")
#         return {"share": share, "status": "Failed"}
    
#     except WebDriverException as e:
#         logging.error(f"[{share}] WebDriver error: {str(e)}")
#         return {"share": share, "status": "Failed", "error": str(e)}
    
#     except Exception as e:
#         logging.error(f"Error scraping {share}: {str(e)}")
#         return {"share": share, "status": "Error", "error": str(e)}

#     finally:
#         session.close()
        # if driver:
        #     try:
        #         driver.quit()
        #     except:
        #         pass










    # def get_all_companies(
    #     self, db: Session, skip: int = 0, limit: int = 10, search: str = None
    # ):
    #     query = db.query(
    #         Company.id,
    #         Company.share_name,
    #         Company.share_symbol,
    #         Company.share_price,
    #         Company.high_low,
    #         Company.bse,
    #         Company.nse,
    #         Company.share_price_percentage
    #     )

    #     if search:
    #         search_filter = or_(
    #             Company.share_name.ilike(f"%{search}%"),
    #             Company.sectore.ilike(f"%{search}%"),
    #             Company.share_symbol.ilike(f"%{search}%")
    #         )
    #         query = query.filter(search_filter)
    #     else:
    #         query = query.filter(Company.share_symbol.in_(NIFTY50_STOCKS))

    #     # Clone query for count (removes ORDER BY if any for performance)
    #     count_query = query.statement.with_only_columns(func.count()).order_by(None)
    #     total_count = db.execute(count_query).scalar()

    #     results = query.offset(skip).limit(limit).all()

    #     return results, total_count











# import json
# import os
# import random
# import regex as re
# import time
# import unicodedata
# from dotenv import load_dotenv
# from datetime import datetime, timedelta

# from bs4 import BeautifulSoup
# import requests

# from fastapi.responses import JSONResponse
# from fastapi import HTTPException

# from server.utils.prompt import gemini_prompt
# from server.db.base import SessionLocal
# from server.models.news import NewsItem

# import google.generativeai as genai
# session = SessionLocal()

# twenty_four_hours_ago = datetime.now() - timedelta(hours=24)
# def normalize_title(title):
#     title = unicodedata.normalize("NFKD", title)
#     title = title.encode("ascii", "ignore").decode("utf-8")
#     title = title.lower()
#     title = re.sub(r'\s+', ' ', title).strip()  # Replace multiple spaces with single space
#     return title

# def is_duplicate_title(title):
#     normalized = normalize_title(title)
#     print(normalized)
#     recent_news = session.query(NewsItem).filter(
#         NewsItem.created_at >= twenty_four_hours_ago
#     ).all()

#     for news in recent_news:
#         if normalize_title(news.title) == normalized:
#             print(news.id)
#             print(news.title)
#             continue

#     return False


# title = "Q4 results today: Wipro, Waaree Renewables among 10 companies to announce earnings on Wednesday"
# if is_duplicate_title(title):
#     print(title)


from datetime import datetime, timedelta
time_to_out_news = "1 hour ago"
if "day ago" in time_to_out_news:
    ago_news = 24.0
elif "hour" in time_to_out_news:
    if "hours" in time_to_out_news:
        ago_news = float(time_to_out_news.replace(" hours ago", ""))
    else:
        ago_news = float(time_to_out_news.replace(" hour ago", ""))

elif "minute" in time_to_out_news:
    if "minutes" in time_to_out_news:
        minutes = float(time_to_out_news.replace(" minutes ago", ""))
        ago_news = minutes / 60
    else:
        minutes = float(time_to_out_news.replace(" minute ago", ""))
        ago_news = minutes / 60
elif "second" in time_to_out_news:
    if "seconds" in time_to_out_news:
        seconds = float(time_to_out_news.replace(" seconds ago", ""))
        ago_news = seconds / 3600
    else:
        seconds = float(time_to_out_news.replace(" second ago", ""))
        ago_news = seconds / 3600

updated_time = datetime.now() - timedelta(hours=ago_news)


print(updated_time)