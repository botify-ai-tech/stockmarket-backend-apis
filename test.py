import logging
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, WebDriverException

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

def scrap_daily1(share):
    all_screener_data_dict = {}

    try:
        logging.info("Starting Ticker scraping")

        # Set Chrome options for headless scraping
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        driver = webdriver.Chrome(options=chrome_options)
        driver.get(f"https://ticker.finology.in/company/{share}")
        time.sleep(2)

        company_essentials_html = driver.find_element(
            By.XPATH,
            "//div[@id='mainContent_divCompanyEssentials']//div[@id='mainContent_updAddRatios']",
        ).get_attribute("outerHTML")
        driver.quit()

        soup = BeautifulSoup(company_essentials_html, "html.parser")
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

        all_screener_data_dict[share] = {
            "Ticker": {
                "Company Essentials": [data]
            }
        }

        essentials = all_screener_data_dict[share]["Ticker"]["Company Essentials"][0]
        print(f"\n📊 Company Overview: {share}")
        print(f"Market Cap        : {essentials.get('Market Cap')}")
        print(f"Enterprise Value  : {essentials.get('Enterprise Value')}")
        print(f"P/B Ratio         : {essentials.get('P/B')}")
        print(f"P/E Ratio         : {essentials.get('P/E')}")
        print(f"Total Debt        : {essentials.get('DEBT')}")
        print(f"Dividend Yield    : {essentials.get('Div. Yield')}")

    except NoSuchElementException:
        logging.error(f"Failed to find elements for {share}")
        return {"share": share, "status": "Failed"}

    except WebDriverException as e:
        logging.error(f"[{share}] WebDriver error: {str(e)}")
        return {"share": share, "status": "Failed", "error": str(e)}

    except Exception as e:
        logging.error(f"Error scraping {share}: {str(e)}")
        return {"share": share, "status": "Error", "error": str(e)}


if __name__ == "__main__":
    scrap_daily1("A2ZINFRA")


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