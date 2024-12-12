from server.db.base import SessionLocal
from dotenv import load_dotenv
import logging
import time
from bs4 import BeautifulSoup
import random
import pandas as pd
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from server.models.ratio import CalculateRatio, Company

load_dotenv()

logging.basicConfig(
    level=logging.INFO,  # Log level (INFO, DEBUG, WARNING, ERROR)
    format="%(asctime)s - %(levelname)s - %(message)s",  # Log format
)

session = SessionLocal()


def daily_sraper():

    all_screener_data_list = []
    all_screener_data_dict = {}

    with open("ratio\\nsc.txt", "r", encoding="utf-8") as f:
        shares = f.readlines()

    for share in shares[25:]:
        share = share.strip("\n")
        # existing_data = session.query(Company).filter(Company.share_symbol == share).first()
        # if existing_data:
        #     print("data is skiped")
        #     continue

        # chrome_options = Options()
        # chrome_options.add_argument("--headless")
        # chrome_options.add_argument("--disable-gpu")
        # chrome_options.add_argument("--window-size=1920,1080")
        # chrome_options.add_argument("--no-sandbox")
        # chrome_options.add_argument("--disable-dev-shm-usage")

        # Initialize the WebDriver with options
        driver = webdriver.Chrome()

        # driver = webdriver.Chrome()
        driver.maximize_window()
        driver.get("https://www.screener.in/")

        # login
        driver.refresh()
        time.sleep(random.randint(1, 10))

        driver.find_element(By.XPATH, "//a[@class='button account']").click()
        email = driver.find_element(By.XPATH, "//input[@id='id_username']")
        email.clear()
        email.send_keys("dharmik301.rejoice@gmail.com")

        password = driver.find_element(By.XPATH, "//input[@id='id_password']")
        password.clear()
        password.send_keys("Dharmik@301")

        driver.find_element(By.XPATH, "//button[@class='button-primary']").click()
        logging.info("Login")

        try:
            driver.refresh()
            time.sleep(random.randint(1, 10))
            driver.refresh()
            search = driver.find_element(
                By.XPATH, "//div[@class='search']//input[@class='u-full-width']"
            )
            search.clear()
            search.send_keys(share)
            time.sleep(random.randint(1, 10))
            search.send_keys(" ")
            time.sleep(1)
            # search.send_keys(Keys.DOWN)
            search.send_keys(Keys.ENTER)
        except:
            pass

        share_name = driver.find_element(
            By.XPATH,
            "//div[@class='card card-large']//div[@class='flex-row flex-wrap flex-align-center flex-grow']//h1[@class='margin-0 show-from-tablet-landscape']",
        ).text
        logging.info(share_name)

        # Share Price
        share_price = driver.find_element(
            By.XPATH,
            "//div[@class='card card-large']//div//div//div[@class='flex flex-align-center']",
        ).text.split("\n")[0]

        # Share Price percentage
        try:
            share_price_percentage = driver.find_element(
                By.XPATH,
                "//span[@class='font-size-12 down margin-left-4']",
            ).text
        except:
            try:
                share_price_percentage = driver.find_element(
                    By.XPATH,
                    "//span[@class='font-size-12 up margin-left-4']",
                ).text
            except:
                share_price_percentage = "0.0%"

        share_info = []

        keys = driver.find_elements(
            By.XPATH,
            "//div[@class='card card-large']//div[@class='company-info']//div[@class='company-ratios']//ul[@id='top-ratios']//li//span[@class='name']",
        )
        values = driver.find_elements(
            By.XPATH,
            "//div[@class='card card-large']//div[@class='company-info']//div[@class='company-ratios']//ul[@id='top-ratios']//li//span[@class='nowrap value']",
        )

        # Create a dictionary for the share info by zipping the keys and values
        share_info = [{key.text: value.text} for key, value in zip(keys, values)]
        share_info_dict = {k: v for d in share_info for k, v in d.items()}

        all_screener_data_dict[share_name] = {}
        all_screener_data_dict[share_name]["Screener"] = {}
        all_screener_data_dict[share_name]["Ticker"] = {}

        all_screener_data_dict[share_name]["Screener"] = {
            "share_name": share_name,
            "share_price": share_price,
            "share_info": share_info_dict,
            "share_price_percentage": share_price_percentage,
        }
        # ------------------------------------------------------------ Peer comparison ------------------------------------------------------------
        logging.info("Peer comparison")

        peer_table_data = []
        for peer_table_index in driver.find_elements(
            By.XPATH,
            "//section[@id='peers']//div//div[@class='responsive-holder fill-card-width']//table//tbody//tr",
        ):
            row_data = [
                th.text for th in peer_table_index.find_elements(By.TAG_NAME, "th")
            ]
            if row_data == [] or row_data == [""]:
                continue
            peer_table_data.append(row_data)

        for peer_table_value in driver.find_elements(
            By.XPATH,
            "//section[@id='peers']//div//div[@class='responsive-holder fill-card-width']//table//tbody//tr",
        ):
            row_data = [
                td.text for td in peer_table_value.find_elements(By.TAG_NAME, "td")
            ]
            if row_data == [] or row_data == [""]:
                continue
            peer_table_data.append(row_data)

        for peer_table_value in driver.find_elements(
            By.XPATH,
            "//section[@id='peers']//div//div[@class='responsive-holder fill-card-width']//table//tfoot//tr",
        ):
            row_data = [
                td.text for td in peer_table_value.find_elements(By.TAG_NAME, "td")
            ]
            if row_data == [] or row_data == [""]:
                continue
            peer_table_data.append(row_data)

        headers = peer_table_data[0]

        # Convert list of lists to list of dictionaries
        json_data = [dict(zip(headers, row)) for row in peer_table_data[1:]]

        # -------------------------------------------- Average P/E ---------------------------------------------------------------------

        total_pe = 0
        count = 0

        for peer_detail in json_data:
            pe_value = peer_detail.get("P/E")
            if pe_value:
                total_pe += float(pe_value)
                count += 1

        average_pe = round(total_pe / count, 2) if count > 0 else 0

        all_screener_data_dict[share_name]["Screener"]["Average P/E"] = average_pe

        # --------------------------------------------profit & loss -----------------------------------------------------------------

        logging.info("Profit & Loss")

        profit_loss = []
        for profit_loss_table_index in driver.find_elements(
            By.XPATH,
            "//section[@id='profit-loss']//div[@class='responsive-holder fill-card-width']//table//thead//tr",
        ):
            row_data = [
                th.text if th.text != "" else "profit loss name"
                for th in profit_loss_table_index.find_elements(By.TAG_NAME, "th")
            ]

            if row_data == []:
                continue
            profit_loss.append(row_data)

        for profit_loss_table_value in driver.find_elements(
            By.XPATH,
            "//section[@id='profit-loss']//div[@class='responsive-holder fill-card-width']//table//tbody//tr",
        ):
            row_data = [
                td.text for td in profit_loss_table_value.find_elements(By.TAG_NAME, "td")
            ]
            if row_data == [] or row_data == [""]:
                continue
            profit_loss.append(row_data)

        try:
            pl_other_table_html = driver.find_element(By.XPATH,"//section[@id='profit-loss']//div[4]").get_attribute("outerHTML")
        except:
            pl_other_table_html = driver.find_element(By.XPATH,"//section[@id='profit-loss']//div[3]").get_attribute("outerHTML")

        soup = BeautifulSoup(pl_other_table_html, 'html.parser')

        # Extract data from each table
        tables = soup.find_all('table', class_='ranges-table')
        data = {}

        # Iterate through each table to extract information
        for table in tables:
            # Extract the title of the table (Compounded Sales Growth, etc.)
            title = table.find('th').get_text().strip()

            # Extract all rows from the table
            rows = table.find_all('tr')[1:]  # Skip the header row

            # Extract the data for each row
            table_data = {}
            for row in rows:
                columns = row.find_all('td')
                if len(columns) == 2:
                    time_period = columns[0].get_text().strip()
                    value = columns[1].get_text().strip()
                    table_data[time_period] = value
            
            # Add the extracted data for the table to the final dictionary
            data[title] = table_data

        profit_loss_headers = profit_loss[0]

        # Convert list of lists to list of dictionaries
        profit_loss_json_data = [
            dict(zip(profit_loss_headers, row)) for row in profit_loss[1:]
        ]

        profit_loss_json_data.append(data)

        all_screener_data_dict[share_name]["Screener"][
            "Profit & Loss"
        ] = profit_loss_json_data

        # -----------------------------------------------------------------------------------------------------------------------
        sectore_link = driver.find_element(By.XPATH, "//section[@id='peers']//div[@class='flex flex-space-between']//p//a[1][@href]").get_attribute("href")
        industry_link = driver.find_element(By.XPATH, "//section[@id='peers']//div[@class='flex flex-space-between']//p//a[2][@href]").get_attribute("href")
        time.sleep(3)
        driver.get(sectore_link)
        try:
            page_numbers = driver.find_elements(By.XPATH, "//div[@class='pagination']//div[@class='flex-baseline options']//a")
            if page_numbers:
                page_number = max([int(max_page_number.text.replace("Next", "0")) for max_page_number in page_numbers])
            else:
                page_number = 1
            print("Total Page Number Industry PE... ", page_number)

            total_data = []
            for i in range(1, page_number+1):
                url = f"{sectore_link}?page={i}"
                res = requests.get(url, headers={"user-agent" : "Custom Agent"})
                time.sleep(0.5)
                extracted_tables = pd.read_html(res.text)
                extracted_tables = extracted_tables[0][extracted_tables[0]['S.No.'] != "S.No."]
                total_data.append(extracted_tables)
            df = pd.concat(total_data)
            df['P/E'] =  pd.to_numeric( df['P/E']) 
            sectore_pe = round(df['P/E'].mean(), 2)
        except:
            res = requests.get(sectore_link, headers={"user-agent" : "Custom Agent"})
            extracted_tables = pd.read_html(res.text)
            extracted_tables = extracted_tables[0][extracted_tables[0]['S.No.'] != "S.No."]
            df = pd.concat([extracted_tables])
            df['P/E'] =  pd.to_numeric(df['P/E']) 
            sectore_pe = round(df['P/E'].mean(), 2)
        
        
        driver.get(industry_link)
        try:
            page_numbers = driver.find_elements(By.XPATH, "//div[@class='pagination']//div[@class='flex-baseline options']//a")
            if page_numbers:
                page_number = max([int(max_page_number.text.replace("Next", "0")) for max_page_number in page_numbers])
            else:
                page_number = 1
            print("Total Page Number Industry PE... ", page_number)

            total_data = []

            for i in range(1, page_number+1):
                url = f"{sectore_link}?page={i}"
                res = requests.get(url, headers={"user-agent" : "Custom Agent"})
                time.sleep(0.5)
                extracted_tables = pd.read_html(res.text)
                extracted_tables = extracted_tables[0][extracted_tables[0]['S.No.'] != "S.No."]
                total_data.append(extracted_tables)

            df = pd.concat(total_data)
            df['P/E'] =  pd.to_numeric( df['P/E']) 
            industry_pe = round(df['P/E'].mean(), 2)    
        except Exception as e:
            res = requests.get(industry_link, headers={"user-agent" : "Custom Agent"})
            time.sleep(3)
            extracted_tables = pd.read_html(res.text)
            extracted_tables = extracted_tables[0][extracted_tables[0]['S.No.'] != "S.No."]
            df = pd.concat([extracted_tables])
            df['P/E'] =  pd.to_numeric(df['P/E']) 
            industry_pe = round(df['P/E'].mean(), 2)

        driver.quit()

        # ----------------------------------------------------------------------------------------------------------------------------------------------------------------
        logging.info("Ticker")
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        # Initialize the WebDriver with options
        driver = webdriver.Chrome(options=chrome_options)

        time.sleep(2)
        # driver = webdriver.Chrome()
        driver.maximize_window()
        driver.get(f"https://ticker.finology.in/company/{share}")

        company_essentials = driver.find_element(
            By.XPATH,
            "//div[@id='mainContent_divCompanyEssentials']//div[@id='mainContent_updAddRatios']",
        ).get_attribute("outerHTML")

        soup = BeautifulSoup(company_essentials, "html.parser")

        data = {}
        company_essentials_detail = []
        # Extract all divs with class 'col-6 col-md-4 compess'
        divs = soup.find_all("div", class_="col-6 col-md-4 compess")

        for div in divs:
            # Extract the label (small text)
            label = div.find("small")
            if label:
                label_text = label.get_text(strip=True)
            # Extract the number value (which is inside a span with class 'Number')
            number_span = div.find("span", class_="Number")
            if number_span:
                number_value = number_span.get_text(strip=True)
            else:
                number_value = "0"
            # Add the extracted data to the dictionary
            if label_text and number_value:
                data[label_text] = number_value

        company_essentials_detail.append(data)

        all_screener_data_dict[share_name]["Ticker"][
            "Company Essentials"
        ] = company_essentials_detail
        driver.quit()

        time.sleep(3)

        market_cap = all_screener_data_dict[share_name]["Screener"]["share_info"].get(
            "Market Cap"
        )
        face_value = all_screener_data_dict[share_name]["Screener"]["share_info"].get(
            "Face Value"
        )
        roe = all_screener_data_dict[share_name]["Screener"]["share_info"].get("ROE")
        stock_pe = all_screener_data_dict[share_name]["Screener"]["share_info"].get(
            "Stock P/E"
        )
        dividend_yield = all_screener_data_dict[share_name]["Screener"][
            "share_info"
        ].get("Dividend Yield")
        roce = all_screener_data_dict[share_name]["Screener"]["share_info"].get("ROCE")
        book_value = all_screener_data_dict[share_name]["Screener"]["share_info"].get(
            "Book Value"
        )
        high_low = all_screener_data_dict[share_name]["Screener"]["share_info"].get(
            "High / Low"
        )

        profit_loss_details = all_screener_data_dict[share_name]["Screener"].get("Profit & Loss")

        debt = all_screener_data_dict[share_name]["Ticker"]["Company Essentials"][
            0
        ].get("DEBT")
        enterprise_value = all_screener_data_dict[share_name]["Ticker"][
            "Company Essentials"
        ][0].get("Enterprise Value")
        eps = all_screener_data_dict[share_name]["Ticker"]["Company Essentials"][
            0
        ].get("EPS (TTM)")
        pb = all_screener_data_dict[share_name]["Ticker"]["Company Essentials"][
            0
        ].get("P/B")
        time.sleep(3)

        exitst_data = (
            session.query(Company).filter(Company.share_symbol == share).first()
        )
        if exitst_data:
            exitst_data.share_price = share_price
            exitst_data.high_low = high_low
            exitst_data.average_pe = average_pe
            exitst_data.share_price_percentage = share_price_percentage
            exitst_data.market_cap = market_cap
            exitst_data.pb_ratio = pb
            exitst_data.eps = eps
            exitst_data.enterprise_value = enterprise_value
            exitst_data.face_value = face_value
            exitst_data.roe = roe
            exitst_data.pe_ratio = stock_pe
            exitst_data.dividend_yield = dividend_yield
            exitst_data.roce = roce
            exitst_data.debt = debt
            exitst_data.book_value = book_value
            exitst_data.s_profit_loss = profit_loss_details
            exitst_data.industry_pe = industry_pe
            exitst_data.sectore_pe = sectore_pe

            session.commit()

            logging.info("Data update in DB")



daily_sraper()
