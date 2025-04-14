from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from server.db.base import SessionLocal
from dotenv import load_dotenv
import logging
import time
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from server.models.ratio import CalculateRatio, Company
from sqlalchemy.exc import SQLAlchemyError
from selenium.common.exceptions import NoSuchElementException, WebDriverException
import os

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

session = SessionLocal()

# Constants
NUM_THREADS = 2
MAX_RETRIES = 3
RETRY_DELAY = 5

# Load share list
with open("ratio/nsc.txt", "r", encoding="utf-8") as f:
    all_shares = [line.strip() for line in f if line.strip()]

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(options=chrome_options)

def scrap_daily1(share):
    try:
        logging.info(f"Starting scraping for: {share}")
        driver = setup_driver()
        driver.get(f"https://ticker.finology.in/company/{share}")
        time.sleep(2)

        essentials_element = driver.find_element(
            By.XPATH,
            "//div[@id='mainContent_divCompanyEssentials']//div[@id='mainContent_updAddRatios']"
        )
        html = essentials_element.get_attribute("outerHTML")
        driver.quit()

        soup = BeautifulSoup(html, "html.parser")
        data = {}
        divs = soup.find_all("div", class_="col-6 col-md-4 compess")

        for div in divs:
            label = div.find("small")
            label_text = label.get_text(strip=True) if label else ""
            number_span = div.find("span", class_="Number")
            number_p = div.find("p")
            number_value = (
                number_span.get_text(strip=True) if number_span
                else number_p.get_text(strip=True) if number_p
                else "0"
            )
            if label_text:
                data[label_text] = number_value

        exitst_data = (
            session.query(Company).filter(Company.share_symbol == share).first()
        )

        if exitst_data:
            exitst_data.market_cap = data.get('Market Cap')
            exitst_data.pb_ratio = data.get('P/B')
            exitst_data.enterprise_value = data.get('Enterprise Value')
            exitst_data.pe_ratio = data.get('P/E')
            exitst_data.dividend_yield = data.get('Div. Yield')
            exitst_data.debt = data.get('DEBT')
            session.commit()

            logging.info(f" {share} Data Updated.")
            return {"share": share, "status": "Success", "data": data}
        else : 
            logging.info(f"{share} Company Not Exist.")
            return {"share": share, "status": "Failed"} 

    except NoSuchElementException:
        logging.error(f"Element not found for {share}")
    except WebDriverException as e:
        logging.error(f"WebDriver error for {share}: {str(e)}")
    except Exception as e:
        logging.error(f"Unexpected error scraping {share}: {str(e)}")
    

    return {"share": share, "status": "Failed"}

def retry_scrap_daily(share):
    for attempt in range(1, MAX_RETRIES + 1):
        result = scrap_daily1(share)
        if result["status"] == "Success":
            return result
        logging.warning(f"[{share}] Attempt {attempt} failed. Retrying in {RETRY_DELAY}s...")
        time.sleep(RETRY_DELAY)
    return {"share": share, "status": "Failed after retries"}

def parallel_scraper(start, end):
    shares_to_scrape = all_shares[start:end]
    unscraped_companies = []

    with ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
        future_to_share = {
            executor.submit(retry_scrap_daily, share): share
            for share in shares_to_scrape
        }

        for future in as_completed(future_to_share):
            result = future.result()
            if result["status"] != "Success":
                unscraped_companies.append(result["share"])
            time.sleep(3)

    return {
        "start": start,
        "end": end,
        "last_update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "unscraped_companies": unscraped_companies
    }

if __name__ == '__main__':
    result = parallel_scraper(0, 2)
    print(result)