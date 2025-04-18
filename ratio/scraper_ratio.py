import time
import random
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
import regex as re
import google.generativeai as genai
from sqlalchemy.exc import SQLAlchemyError
from selenium.common.exceptions import NoSuchElementException

from server.config import settings
from server.models.ratio import CalculateRatio, Company
from server.utils.money_control.other_ratios import (
    coverage_ratios,
    efficiency_ratios,
    financial_ratios,
    growth_ratios,
    liquidity_ratios,
    profitability_ratios,
    solvency_ratios,
    valuation_ratios,
)
from dotenv import load_dotenv
import logging

from server.utils.prompt import ratio_prompt
from ticker import ticker
from server.db.base import SessionLocal

load_dotenv()

gemini_ai_key = settings.GEMINI_AI_KEY
genai.configure(api_key=gemini_ai_key)

logging.basicConfig(
    level=logging.INFO,  # Log level (INFO, DEBUG, WARNING, ERROR)
    format="%(asctime)s - %(levelname)s - %(message)s",  # Log format
)

session = SessionLocal()




def ration(share):

    all_screener_data_list = []
    all_screener_data_dict = {}

    
    try :
        # with open("ratio\\nsc.txt", "r", encoding="utf-8") as f:
        #     shares = f.readlines()

        # for share in shares[740:]:
        #     share = share.strip("\n")
            # existing_data = session.query(Company).filter(Company.share_symbol == share).first()
            # if existing_data:
            #     print("data is skiped")
            #     continue

        chrome_options = Options()
        chrome_options.add_argument("--headless")  
        chrome_options.add_argument("--disable-gpu") 
        chrome_options.add_argument("--window-size=1920,1080") 
        chrome_options.add_argument("--no-sandbox")  
        chrome_options.add_argument("--disable-dev-shm-usage")

        # Initialize the WebDriver with options
        driver = webdriver.Chrome(options=chrome_options)


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

        # ------------------------------------------------------------ Share details ------------------------------------------------------------
        logging.info("Share details")
        driver.refresh()
        time.sleep(random.randint(1, 10))
        # Share Name
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

        # date
        date = driver.find_element(
            By.XPATH, "//div[@class='card card-large']//div//div//div[2]//div[2]"
        ).text

        try:
            # BSC
            bsc = driver.find_element(
                By.XPATH,
                "//div[@class='card card-large']//div[@class='company-links show-from-tablet-landscape']//a[2]",
            ).text

            bse_kay = bsc.split(":")[0]
            bse_value = bsc.split(":")[1]

        except:
            pass

        try:
            # NSE
            nsc = driver.find_element(
                By.XPATH,
                "//div[@class='card card-large']//div[@class='company-links show-from-tablet-landscape']//a[3]",
            ).text
            nse_kay = nsc.split(":")[0]
            nse_value = nsc.split(":")[1]
        except:
            pass

        try:
            # time.sleep(random.randint(1, 10))
            driver.find_element(
                By.XPATH,
                "//div[@class='card card-large']//div[@class='company-info']//div[@class='company-profile']//div[@class='sub show-more-box about']//button//i",
            ).click()
        except:
            pass

        # About Company
        about_company = []
        for about in driver.find_elements(
            By.XPATH,
            "//div[@class='card card-large']//div[@class='company-info']//div[@class='company-profile']//div[@class='sub show-more-box about highlight']//p",
        ):
            about_company.append(about.text)

        try:
            company_info_link = []
            if driver.find_element(
                By.XPATH,
                "//div[@class='card card-large']//div[@class='company-info']//div[@class='company-profile']//div[@class='sub show-more-box about highlight']//sup//a[@href]",
            ):
                for company_information_docs in driver.find_elements(
                    By.XPATH,
                    "//div[@class='card card-large']//div[@class='company-info']//div[@class='company-profile']//div[@class='sub show-more-box about highlight']//sup//a[@href]",
                ):
                    company_info_link.append(company_information_docs.get_attribute("href"))
        except:
            pass

        # Key Points
        key_points = []
        for point in driver.find_elements(
            By.XPATH,
            "//div[@class='card card-large']//div[@class='company-info']//div[@class='company-profile']//div[@class='sub commentary always-show-more-box']//p",
        ):
            key_points.append(point.text)

        try:
            key_points_link = []
            for key_point_link in driver.find_elements(
                By.XPATH,
                "//div[@class='card card-large']//div[@class='company-info']//div[@class='company-profile']//div[@class='sub commentary always-show-more-box']//sup//a[@href]",
            ):
                key_points_link.append(key_point_link.get_attribute("href"))
        except:
            pass

        time.sleep(1)
        # share info
        share_info = []
        share_keys = []
        share_values = []

        # time.sleep(random.randint(1, 10))
        for share_key_detail in driver.find_elements(
            By.XPATH,
            "//div[@class='card card-large']//div[@class='company-info']//div[@class='company-ratios']//ul[@id='top-ratios']//li//span[@class='name']",
        ):
            share_keys.append(share_key_detail.text)
        for share_value_detail in driver.find_elements(
            By.XPATH,
            "//div[@class='card card-large']//div[@class='company-info']//div[@class='company-ratios']//ul[@id='top-ratios']//li//span[@class='nowrap value']",
        ):
            share_values.append(share_value_detail.text)

        for share_keys, share_values in zip(share_keys, share_values):
            share_info.append({share_keys: share_values})

        all_screener_data_dict[share_name] = {}
        all_screener_data_dict[share_name]["Screener"] = {}

        all_screener_data_dict[share_name]["Screener"] = {
            "share_name": share_name,
            "share_price": share_price,
            "date": date,
            "about_company": about_company,
            "key_points": key_points,
            "company_information_docs": {
                "about": company_info_link,
                "key_points": key_points_link,
            },
            "share_info": share_info,
        }
        try:
            if bse_kay and bse_value:
                all_screener_data_dict[share_name]["Screener"][bse_kay] = bse_value
        except:
            pass
        try:
            if nse_kay and nse_value:
                all_screener_data_dict[share_name]["Screener"][nse_kay] = nse_value
        except:
            pass

        # ------------------------------------------------------------ Chart -------------------------------------------------------------
        logging.info("Chart")

        # time.sleep(random.randint(1, 10))
        chart_wait = WebDriverWait(driver, 10)
        chart_wait.until(
            lambda driver: driver.find_element(
                By.XPATH,
                "//section[@id='chart']//div[@class='flex margin-bottom-24']//button[2]",
            )
        )
        pe_ration = driver.find_element(
            By.XPATH,
            "//section[@id='chart']//div[@class='flex margin-bottom-24']//button[2]",
        )
        pe_ration.click()
        time.sleep(0.5)
        pe_ration.click()

        chat_time_list = []
        chat_median_pe = []
        try:
            for chat_time in driver.find_elements(
                By.XPATH, "//section[@id='chart']//div[@class='options']//button"
            ):
                chat_time.click()
                time.sleep(0.5)
                chat_time.click()
                time.sleep(0.5)
                chat_time.click()
                chat_time_list.append(chat_time.text)
                # time.sleep(random.randint(1, 10))
                median_pe = driver.find_element(
                    By.XPATH, "//section[@id='chart']//div[@class='flex']//label[2]"
                ).text
                chat_median_pe.append(median_pe.split("=")[1])

            chart_median = []
            for chat_time_list, chat_median_pe in zip(chat_time_list, chat_median_pe):
                chart_median.append({"time": chat_time_list, "Median PE": chat_median_pe})

            all_screener_data_dict[share_name]["Screener"]["Chart"] = chart_median
        except:
            all_screener_data_dict[share_name]["Screener"]["Chart"] = []


        # ------------------------------------------------------------ Analysis ------------------------------------------------------------
        logging.info("Analysis")

        pros = driver.find_element(By.XPATH, "//section[@id='analysis']//div//div//ul").text

        cons = driver.find_element(
            By.XPATH, "//section[@id='analysis']//div//div[@class='cons']//ul"
        ).text

        all_screener_data_dict[share_name]["Screener"]["analysis"] = {
            "pros": pros,
            "cons": cons,
        }
        # ----------------------------------------------------------- Expanded view -----------------------------------------------------------
        logging.info("Expanded view")
        for button in driver.find_elements(
            By.XPATH,
            "//table[@class='data-table responsive-text-nowrap']//tbody//tr//td//button",
        ):
                button.click()

        # ----------------------------------------------------- Sectore & industry ---------------------------------------------------------
        logging.info("sectore & industry")
        sectore = driver.find_element(By.XPATH, "//div[@class='flex flex-space-between']//div//p//a[1]").text
        industry = driver.find_element(By.XPATH, "//div[@class='flex flex-space-between']//div//p//a[2]").text
        all_screener_data_dict[share_name]["Screener"]["sectore"] = sectore
        all_screener_data_dict[share_name]["Screener"]["industry"] = industry

        # ------------------------------------------------------------ Peer comparison ------------------------------------------------------------
        logging.info("Peer comparison")

        peer_table_data = []
        for peer_table_index in driver.find_elements(
            By.XPATH,
            "//section[@id='peers']//div//div[@class='responsive-holder fill-card-width']//table//tbody//tr",
        ):
            row_data = [th.text for th in peer_table_index.find_elements(By.TAG_NAME, "th")]
            if row_data == [] or row_data == [""]:
                continue
            peer_table_data.append(row_data)

        for peer_table_value in driver.find_elements(
            By.XPATH,
            "//section[@id='peers']//div//div[@class='responsive-holder fill-card-width']//table//tbody//tr",
        ):
            row_data = [td.text for td in peer_table_value.find_elements(By.TAG_NAME, "td")]
            if row_data == [] or row_data == [""]:
                continue
            peer_table_data.append(row_data)

        for peer_table_value in driver.find_elements(
            By.XPATH,
            "//section[@id='peers']//div//div[@class='responsive-holder fill-card-width']//table//tfoot//tr",
        ):
            row_data = [td.text for td in peer_table_value.find_elements(By.TAG_NAME, "td")]
            if row_data == [] or row_data == [""]:
                continue
            peer_table_data.append(row_data)

        headers = peer_table_data[0]

        # Convert list of lists to list of dictionaries
        json_data = [dict(zip(headers, row)) for row in peer_table_data[1:]]

        all_screener_data_dict[share_name]["Screener"]["Peer comparison"] = json_data

        # -------------------------------------------- Average P/E ---------------------------------------------------------------------
        peer_details = all_screener_data_dict[share_name]["Screener"]["Peer comparison"]
        total_pe = 0
        count = 0

        for peer_detail in peer_details:
            pe_value = peer_detail.get("P/E")
            if pe_value:
                total_pe += float(pe_value)
                count += 1

        average_pe = round(total_pe / count, 2) if count > 0 else 0

        all_screener_data_dict[share_name]["Screener"]["Average P/E"] = average_pe

        # ------------------------------------------------------------ Quarterly Results ------------------------------------------------------------
        logging.info("Quarterly Results")

        quarterly_results = []
        for quarterly_table_index in driver.find_elements(
            By.XPATH,
            "//section[@id='quarters']//div[@class='responsive-holder fill-card-width']//table//thead//tr",
        ):
            row_data = [
                th.text if th.text != "" else "quarterly name"
                for th in quarterly_table_index.find_elements(By.TAG_NAME, "th")
            ]

            if row_data == []:
                continue
            quarterly_results.append(row_data)

        for quarterly_table_value in driver.find_elements(
            By.XPATH,
            "//section[@id='quarters']//div[@class='responsive-holder fill-card-width']//table//tbody//tr",
        ):
            row_data = []
            for td in quarterly_table_value.find_elements(By.TAG_NAME, "td"):
                # Check if there is an 'a' tag inside the 'td'
                a_tag = (
                    td.find_element(By.TAG_NAME, "a")
                    if td.find_elements(By.TAG_NAME, "a")
                    else None
                )
                if a_tag:
                    # Append both text and href as a tuple
                    row_data.append(a_tag.get_attribute("href"))
                else:
                    row_data.append(td.text)

            if not row_data or row_data == [""]:
                continue
            quarterly_results.append(row_data)

        quarterly_headers = quarterly_results[0]

        # Convert list of lists to list of dictionaries
        quarterly_json_data = [
            dict(zip(quarterly_headers, row)) for row in quarterly_results[1:]
        ]

        all_screener_data_dict[share_name]["Screener"][
            "Quarterly Results"
        ] = quarterly_json_data

        # ------------------------------------------------------------- Profit & Loss -------------------------------------------------------------
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

        # driver.refresh()
        # profit_loss_other_table = []
        # for profit_loss_table_other_index in driver.find_elements(By.XPATH,"//section[@id='profit-loss']//div[3]//table[@class='ranges-table']//tbody//tr",):
        #     profit_loss_other_table.append(profit_loss_table_other_index.text)

        # structured_data = {}
        # breakpoint()
        # # Helper function to extract the periods and values
        # def extract_period_values(values):
        #     return {period.split(": ")[0]: period.split(": ")[1] for period in values}

        # # Iterate over the data_list and structure the data
        # time.sleep(random.randint(1, 15))
        # i = 0
        # while i < len(profit_loss_other_table):
        #     key = profit_loss_other_table[i]
        #     values = []
        #     i += 1
        #     while i < len(profit_loss_other_table) and ":" in profit_loss_other_table[i]:
        #         values.append(profit_loss_other_table[i])
        #         i += 1
        #     structured_data[key] = extract_period_values(values)

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

        # ------------------------------------------------------------- Balance Sheet -------------------------------------------------------------
        logging.info("Balance Sheet")

        balance_sheet = []
        for balance_sheet_table_index in driver.find_elements(
            By.XPATH,
            "//section[@id='balance-sheet']//div[@class='responsive-holder fill-card-width']//table//thead//tr",
        ):
            row_data = [
                th.text if th.text != "" else "balance sheet name"
                for th in balance_sheet_table_index.find_elements(By.TAG_NAME, "th")
            ]

            if row_data == []:
                continue
            balance_sheet.append(row_data)

        for balance_sheet_table_value in driver.find_elements(
            By.XPATH,
            "//section[@id='balance-sheet']//div[@class='responsive-holder fill-card-width']//table//tbody//tr",
        ):
            row_data = [
                td.text for td in balance_sheet_table_value.find_elements(By.TAG_NAME, "td")
            ]

            if not row_data or row_data == [""]:
                continue
            balance_sheet.append(row_data)

        balance_sheet_headers = balance_sheet[0]

        # Convert list of lists to list of dictionaries
        balance_sheet_json_data = [
            dict(zip(balance_sheet_headers, row)) for row in balance_sheet[1:]
        ]

        all_screener_data_dict[share_name]["Screener"][
            "Balance Sheet"
        ] = balance_sheet_json_data

        # ------------------------------------------------------------- Cash Flows -------------------------------------------------------------
        logging.info("Cash Flows")

        cash_flows = []
        for cash_flows_table_index in driver.find_elements(
            By.XPATH,
            "//section[@id='cash-flow']//div[@class='responsive-holder fill-card-width']//table//thead//tr",
        ):
            row_data = [
                th.text if th.text != "" else "cash flows name"
                for th in cash_flows_table_index.find_elements(By.TAG_NAME, "th")
            ]

            if row_data == []:
                continue
            cash_flows.append(row_data)

        for cash_flows_table_value in driver.find_elements(
            By.XPATH,
            "//section[@id='cash-flow']//div[@class='responsive-holder fill-card-width']//table//tbody//tr",
        ):
            row_data = [
                td.text for td in cash_flows_table_value.find_elements(By.TAG_NAME, "td")
            ]

            if not row_data or row_data == [""]:
                continue
            cash_flows.append(row_data)

        cash_flows_headers = cash_flows[0]

        # Convert list of lists to list of dictionaries
        cash_flows_json_data = [
            dict(zip(cash_flows_headers, row)) for row in cash_flows[1:]
        ]

        all_screener_data_dict[share_name]["Screener"]["Cash Flows"] = cash_flows_json_data

        # ------------------------------------------------------------- Ratios -------------------------------------------------------------
        logging.info("Ratios")


        ratios = []
        for ratios_table_index in driver.find_elements(
            By.XPATH,
            "//section[@id='ratios']//div[@class='responsive-holder fill-card-width']//table//thead//tr",
        ):
            row_data = [
                th.text if th.text != "" else "ratios name"
                for th in ratios_table_index.find_elements(By.TAG_NAME, "th")
            ]

            if row_data == []:
                continue
            ratios.append(row_data)

        for ratios_table_value in driver.find_elements(
            By.XPATH,
            "//section[@id='ratios']//div[@class='responsive-holder fill-card-width']//table//tbody//tr",
        ):
            row_data = [
                td.text for td in ratios_table_value.find_elements(By.TAG_NAME, "td")
            ]

            if not row_data or row_data == [""]:
                continue
            ratios.append(row_data)

        ratios_headers = ratios[0]

        # Convert list of lists to list of dictionaries
        ratios_json_data = [dict(zip(ratios_headers, row)) for row in ratios[1:]]

        all_screener_data_dict[share_name]["Screener"]["Ratios"] = ratios_json_data

        # ------------------------------------------------------------- Shareholding Pattern -------------------------------------------------------------
        logging.info("Shareholding Pattern")

        # ===================== Quarterly =====================
        shareholding_pattern_quarterly = []
        shareholding_pattern_dict = {}
        shareholding_pattern_dict["Quarterly"] = {}
        shareholding_pattern_dict["Yearly"] = {}
        try:
            for shareholding_pattern_table_index in driver.find_elements(
                By.XPATH,
                "//section[@id='shareholding']//div[@id='quarterly-shp']//div[@class='responsive-holder fill-card-width']//table//thead//tr",
            ):
                row_data = [
                    th.text if th.text != "" else "shareholding pattern name"
                    for th in shareholding_pattern_table_index.find_elements(By.TAG_NAME, "th")
                ]

                if row_data == []:
                    continue
                shareholding_pattern_quarterly.append(row_data)

            for shareholding_pattern_table_value in driver.find_elements(
                By.XPATH,
                "//section[@id='shareholding']//div[@id='quarterly-shp']//div[@class='responsive-holder fill-card-width']//table//tbody//tr",
            ):
                row_data = [
                    td.text
                    for td in shareholding_pattern_table_value.find_elements(By.TAG_NAME, "td")
                ]

                if not row_data or row_data == [""]:
                    continue
                shareholding_pattern_quarterly.append(row_data)

            shareholding_pattern_headers_q = shareholding_pattern_quarterly[0]

            shareholding_pattern_dict["Quarterly"] = [
                dict(zip(shareholding_pattern_headers_q, row))
                for row in shareholding_pattern_quarterly[1:]
            ]

            # ===================== Yearly =====================
            # click on yearly button
            driver.find_element(
                By.XPATH,
                "//section[@id='shareholding']//div[@class='options small margin-0']//button[2]",
            ).click()

            shareholding_pattern_yearly = []
            for shareholding_pattern_table_index_y in driver.find_elements(
                By.XPATH,
                "//section[@id='shareholding']//div[@id='yearly-shp']//div[@class='responsive-holder fill-card-width']//table//thead//tr",
            ):
                row_data = [
                    th.text if th.text != "" else "shareholding pattern name"
                    for th in shareholding_pattern_table_index_y.find_elements(
                        By.TAG_NAME, "th"
                    )
                ]

                if row_data == []:
                    continue
                shareholding_pattern_yearly.append(row_data)

            for shareholding_pattern_table_value_y in driver.find_elements(
                By.XPATH,
                "//section[@id='shareholding']//div[@id='yearly-shp']//div[@class='responsive-holder fill-card-width']//table//tbody//tr",
            ):
                row_data = [
                    td.text
                    for td in shareholding_pattern_table_value_y.find_elements(
                        By.TAG_NAME, "td"
                    )
                ]

                if not row_data or row_data == [""]:
                    continue
                shareholding_pattern_yearly.append(row_data)

            shareholding_pattern_headers_y = shareholding_pattern_yearly[0]

            shareholding_pattern_dict["Yearly"] = [
                dict(zip(shareholding_pattern_headers_y, row))
                for row in shareholding_pattern_yearly[1:]
            ]
        except:
            pass
        all_screener_data_dict[share_name]["Screener"][
            "Shareholding Pattern"
        ] = shareholding_pattern_dict

        # -------------------------------------------------------------- Documents -------------------------------------------------------------
        logging.info("Documents")
        driver.refresh()
        # ========= announcements =========
        documents_dict = {}
        announcements_list = []

        documents_dict["Announcements"] = {}

        for announcements_table in driver.find_elements(
            By.XPATH,
            "//section[@id='documents']//div[@class='flex-row flex-gap-small']//div[@id='company-announcements-tab']//ul//li//a[@href]",
        ):
            announcements_list.append(announcements_table.get_attribute("href"))

        documents_dict["Announcements"]["recent"] = announcements_list

        # ========= annual reports =========
        logging.info("annual reports")
        driver.refresh()
        annual_reports_link = []
        annual_reports_text = []

        annual_reports_data = []

        try:
            # time.sleep(random.randint(1, 10))
            driver.find_element(
                By.XPATH,
                "//section[@id='documents']//div[@class='flex-row flex-gap-small']//div[@class='documents annual-reports flex-column']//button//i",
            ).click()
        except:
            pass

        for annual_reports_table in driver.find_elements(
            By.XPATH,
            "//section[@id='documents']//div[@class='flex-row flex-gap-small']//div[@class='documents annual-reports flex-column']//ul//li//a[@href]",
        ):
            annual_reports_link.append(annual_reports_table.get_attribute("href"))

        for annual_reports_link_text in driver.find_elements(
            By.XPATH,
            "//section[@id='documents']//div[@class='flex-row flex-gap-small']//div[@class='documents annual-reports flex-column']//ul//li//a",
        ):
            time.sleep(0.5)
            annual_reports_text.append(annual_reports_link_text.text.replace("\n", "-"))

        for annual_reports_link, annual_reports_text in zip(
            annual_reports_link, annual_reports_text
        ):
            annual_reports_data.append({annual_reports_text: annual_reports_link})

        documents_dict["Annual Reports"] = annual_reports_data

        # ========= Credit ratings =========

        credit_rating_link = []
        credit_rating_text = []

        credit_rating_data = []

        for credit_rating_table in driver.find_elements(
            By.XPATH,
            "//section[@id='documents']//div[@class='flex-row flex-gap-small']//div[@class='documents credit-ratings flex-column']//ul//li//a[@href]",
        ):
            credit_rating_link.append(credit_rating_table.get_attribute("href"))

        for credit_rating_link_text in driver.find_elements(
            By.XPATH,
            "//section[@id='documents']//div[@class='flex-row flex-gap-small']//div[@class='documents credit-ratings flex-column']//ul//li//a",
        ):
            credit_rating_text.append(credit_rating_link_text.text.replace("\n", "-"))

        for credit_rating_link, credit_rating_text in zip(
            credit_rating_link, credit_rating_text
        ):
            credit_rating_data.append({credit_rating_text: credit_rating_link})

        documents_dict["Credit ratings"] = credit_rating_data

        # ========= Concalls ==========

        html_content = driver.page_source
        try:
            soup = BeautifulSoup(html_content, "html.parser")
            concalls_section = soup.find("div", class_="documents concalls flex-column")
            concalls = []

            for li in concalls_section.find_all("li", class_="flex flex-gap-8 flex-wrap"):
                date = li.find(
                    "div", class_="ink-600 font-size-15 font-weight-500 nowrap"
                ).text.strip()
                links = []
                for a in li.find_all("a", class_="concall-link"):
                    link_text = a.text.strip()
                    link_href = a["href"]
                    links.append({link_text: link_href})
                    # links.append({'text': link_text, 'href': link_href})
                concalls.append({"date": date, "links": links})

            documents_dict["Concalls"] = concalls

        except:
            pass
        all_screener_data_dict[share_name]["Screener"]["Documents"] = {}
        all_screener_data_dict[share_name]["Screener"]["Documents"] = documents_dict

        driver.quit()
        # ------------------------------------------------------------ Ticker -----------------------------------------------------------------------
        ticker_details = ticker(share)
        all_screener_data_dict[share_name]["Ticker"] = ticker_details

        current_date = all_screener_data_dict[share_name]["Screener"]["date"]
        market_cap = all_screener_data_dict[share_name]["Screener"]["share_info"][0][
            "Market Cap"
        ]
        high_low = all_screener_data_dict[share_name]["Screener"]["share_info"][2][
            "High / Low"
        ]
        sectore = all_screener_data_dict[share_name]["Screener"]["sectore"]
        industry = all_screener_data_dict[share_name]["Screener"]["industry"] 
        pe_ratio = all_screener_data_dict[share_name]["Screener"]["share_info"][3][
            "Stock P/E"
        ]
        # about_doc  = all_screener_data_dict[share_name]["Screener"]["company_information_docs"]["about"][0]
        average_pe = all_screener_data_dict[share_name]["Screener"]["Average P/E"]

        enterprise_value = all_screener_data_dict[share_name]["Ticker"][0]["Company Essentials"][0].get("Enterprise Value", None)
        p_b = all_screener_data_dict[share_name]["Ticker"][0]["Company Essentials"][0].get("P/B", None)
        book_value = all_screener_data_dict[share_name]["Screener"]["share_info"][4][
            "Book Value"
        ]
        dividend_yield = all_screener_data_dict[share_name]["Screener"]["share_info"][5][
            "Dividend Yield"
        ]
        promoter_holding = all_screener_data_dict[share_name]["Ticker"][0][
            "Company Essentials"
        ][0]["Promoter Holding"]
        eps = all_screener_data_dict[share_name]["Ticker"][0]["Company Essentials"][0][
            "EPS (TTM)"
        ]
        sales_growth = all_screener_data_dict[share_name]["Ticker"][0][
            "Company Essentials"
        ][0].get("Sales Growth")
        profit_growth = all_screener_data_dict[share_name]["Ticker"][0][
            "Company Essentials"
        ][0]["Profit Growth"]
        roce = all_screener_data_dict[share_name]["Ticker"][0]["Company Essentials"][0][
            "ROCE"
        ]
        cash = all_screener_data_dict[share_name]["Ticker"][0]["Company Essentials"][0].get(
            "CASH"
        )
        debt = all_screener_data_dict[share_name]["Ticker"][0]["Company Essentials"][0].get(
            "DEBT"
        )
        roe = all_screener_data_dict[share_name]["Ticker"][0]["Company Essentials"][0][
            "ROE"
        ]
        face_value = all_screener_data_dict[share_name]["Screener"]["share_info"][8][
            "Face Value"
        ]
        bse = all_screener_data_dict[share_name]["Screener"].get("BSE")
        nse = all_screener_data_dict[share_name]["Screener"].get("NSE")
        chart = all_screener_data_dict[share_name]["Screener"]["Chart"]
        s_pros = all_screener_data_dict[share_name]["Screener"]["analysis"]["pros"]
        s_cons = all_screener_data_dict[share_name]["Screener"]["analysis"]["cons"]
        s_peer_comparison = all_screener_data_dict[share_name]["Screener"][
            "Peer comparison"
        ]
        s_quarterly_results = all_screener_data_dict[share_name]["Screener"][
            "Quarterly Results"
        ]
        s_profit_loss = all_screener_data_dict[share_name]["Screener"]["Profit & Loss"]
        s_balance_sheet = all_screener_data_dict[share_name]["Screener"]["Balance Sheet"]
        s_cash_flows = all_screener_data_dict[share_name]["Screener"]["Cash Flows"]
        s_ratios = all_screener_data_dict[share_name]["Screener"]["Ratios"]
        s_shareholding_pattern_quarterly = all_screener_data_dict[share_name]["Screener"][
            "Shareholding Pattern"
        ]["Quarterly"]
        s_shareholding_pattern_yearly = all_screener_data_dict[share_name]["Screener"][
            "Shareholding Pattern"
        ]["Yearly"]
        s_documents = all_screener_data_dict[share_name]["Screener"]["Documents"]
        t_strengths = all_screener_data_dict[share_name]["Ticker"][0]["Strengths"]
        t_limitations = all_screener_data_dict[share_name]["Ticker"][0]["Limitations"]
        t_quarterly_results = all_screener_data_dict[share_name]["Ticker"][0][
            "Quarterly Result"
        ]
        t_profit_loss = all_screener_data_dict[share_name]["Ticker"][0]["Profit & Loss"]
        t_profit_loss = all_screener_data_dict[share_name]["Ticker"][0]["Profit & Loss"]
        t_balance_sheet_equity_and_liabilities = all_screener_data_dict[share_name][
            "Ticker"
        ][0]["Balance Sheet"][0]["Equity and Liabilities"]
        t_balance_sheet_assets = all_screener_data_dict[share_name]["Ticker"][0][
            "Balance Sheet"
        ][0]["Assets"]
        t_cash_flows = all_screener_data_dict[share_name]["Ticker"][0].get("Cash Flows")

        

        ratio_details_list = []
        ratio_details_dict = {}
        ratio_details_dict["ration"] = {}

        liquidity_ratios_data = liquidity_ratios(all_screener_data_dict, share_name)
        ratio_details_dict["ration"].update(
            {"liquidity_ratios_data": liquidity_ratios_data}
        )

        solvency_ratios_data = solvency_ratios(all_screener_data_dict, share_name)
        ratio_details_dict["ration"].update({"solvency_ratios_data": solvency_ratios_data})

        efficiency_ratios_data = efficiency_ratios(all_screener_data_dict, share_name)
        ratio_details_dict["ration"].update(
            {"efficiency_ratios_data": efficiency_ratios_data}
        )

        growth_ratios_data = growth_ratios(all_screener_data_dict, share_name)
        ratio_details_dict["ration"].update({"growth_ratios_data": growth_ratios_data})

        coverage_ratios_data = coverage_ratios(all_screener_data_dict, share_name)
        ratio_details_dict["ration"].update({"coverage_ratios_data": coverage_ratios_data})

        financial_ratios_data = financial_ratios(all_screener_data_dict, share_name)
        ratio_details_dict["ration"].update(
            {"financial_ratios_data": financial_ratios_data}
        )

        profitability_ratios_data = profitability_ratios(all_screener_data_dict, share_name)
        ratio_details_dict["ration"].update(
            {"profitability_ratios_data": profitability_ratios_data}
        )

        valuation_ratios_data = valuation_ratios(all_screener_data_dict, share_name)
        ratio_details_dict["ration"].update({"valuation_ratios": valuation_ratios_data})


        existing_company = (
            session.query(Company)
            .filter(Company.share_symbol == share)
            .first()
        )

        if existing_company:
            # Update existing record
            existing_company.share_name = share_name
            existing_company.current_date = current_date
            existing_company.share_price = share_price
            existing_company.market_cap = market_cap
            existing_company.high_low = high_low
            existing_company.pe_ratio = pe_ratio
            existing_company.pb_ratio = p_b
            existing_company.enterprise_value = enterprise_value
            existing_company.book_value = book_value
            existing_company.dividend_yield = dividend_yield
            existing_company.promoter_holding = promoter_holding
            existing_company.eps = eps
            existing_company.average_pe = average_pe
            existing_company.sectore = sectore
            existing_company.industry = industry
            existing_company.sales_growth = sales_growth
            existing_company.profit_growth = profit_growth
            existing_company.roce = roce
            existing_company.cash = cash
            existing_company.debt = debt
            existing_company.roe = roe
            existing_company.face_value = face_value
            existing_company.bse = bse
            existing_company.nse = nse
            existing_company.chart = chart
            existing_company.s_pros = s_pros
            existing_company.s_cons = s_cons
            existing_company.s_peer_comparison = s_peer_comparison
            existing_company.s_quarterly_results = s_quarterly_results
            existing_company.s_profit_loss = s_profit_loss
            existing_company.s_balance_sheet = s_balance_sheet
            existing_company.s_cash_flows = s_cash_flows
            existing_company.s_ratios = s_ratios
            existing_company.s_shareholding_pattern_quarterly = s_shareholding_pattern_quarterly
            existing_company.s_shareholding_pattern_yearly = s_shareholding_pattern_yearly
            existing_company.s_documents = s_documents
            existing_company.t_strengths = t_strengths
            existing_company.t_limitations = t_limitations
            existing_company.t_quarterly_results = t_quarterly_results
            existing_company.t_profit_loss = t_profit_loss
            existing_company.t_balance_sheet_equity_and_liabilities = t_balance_sheet_equity_and_liabilities
            existing_company.t_balance_sheet_assets = t_balance_sheet_assets
            existing_company.t_cash_flows = t_cash_flows

            logging.info("Company Data Updated.")

        else:
            company_entry = Company(
                share_name=share_name,
                current_date=current_date,
                share_symbol=share,
                share_price=share_price,
                compnay_info_doc=None,
                market_cap=market_cap,
                high_low=high_low,
                pe_ratio=pe_ratio,
                pb_ratio=p_b,
                enterprise_value=enterprise_value,
                book_value=book_value,
                dividend_yield=dividend_yield,
                promoter_holding=promoter_holding,
                eps=eps,
                average_pe=average_pe,
                sectore=sectore,
                industry=industry,
                sales_growth=sales_growth,
                profit_growth=profit_growth,
                roce=roce,
                cash=cash,
                debt=debt,
                roe=roe,
                face_value=face_value,
                bse=bse,
                nse=nse,
                chart=chart,
                s_pros=s_pros,
                s_cons=s_cons,
                s_peer_comparison=s_peer_comparison,
                s_quarterly_results=s_quarterly_results,
                s_profit_loss=s_profit_loss,
                s_balance_sheet=s_balance_sheet,
                s_cash_flows=s_cash_flows,
                s_ratios=s_ratios,
                s_shareholding_pattern_quarterly=s_shareholding_pattern_quarterly,
                s_shareholding_pattern_yearly=s_shareholding_pattern_yearly,
                s_documents=s_documents,
                t_strengths=t_strengths,
                t_limitations=t_limitations,
                t_quarterly_results=t_quarterly_results,
                t_profit_loss=t_profit_loss,
                t_balance_sheet_equity_and_liabilities=t_balance_sheet_equity_and_liabilities,
                t_balance_sheet_assets=t_balance_sheet_assets,
                t_cash_flows=t_cash_flows,
            )

            session.add(company_entry)

            logging.info("Company Data Inserted.")
        session.commit()
        
    # -----------------------------------------------------------------------------------
        ratio_details_list.append(ratio_details_dict)
    # -----------------------------------------------------------------------------------

        existing_ratio = (
            session.query(CalculateRatio)
            .filter(CalculateRatio.share_symbol == share)
            .first()
        )
        if existing_ratio:
            # Update existing record instead of creating a new one
            existing_ratio.liquidity_ratio = liquidity_ratios_data
            existing_ratio.solvency_ratio = solvency_ratios_data
            existing_ratio.efficiency_ratio = efficiency_ratios_data
            existing_ratio.growth_ratio = growth_ratios_data
            existing_ratio.coverage_ratio = coverage_ratios_data
            existing_ratio.financial_ratio = financial_ratios_data
            existing_ratio.profitability_ratio = profitability_ratios_data
            existing_ratio.valuation_ratios = valuation_ratios_data

            logging.info("CalculateRatio Data Updated.")
        else:
            claculate_ratio = CalculateRatio(
                company_id=company_entry.id,
                share_symbol=share,
                liquidity_ratio=liquidity_ratios_data,
                solvency_ratio=solvency_ratios_data,
                efficiency_ratio=efficiency_ratios_data,
                growth_ratio=growth_ratios_data,
                coverage_ratio=coverage_ratios_data,
                financial_ratio=financial_ratios_data,
                profitability_ratio=profitability_ratios_data,
                valuation_ratios=valuation_ratios_data,
            )
            session.add(claculate_ratio)

            logging.info("CalculateRatio Data Inserted.")
        session.commit()

        return {
            "status": 200,
            "message": "Data Inserted Successfully",
        }
        # ------------------------------------------------------- Save the data -------------------------------------------------------

    #     all_screener_data_list.append(
    #         {
    #             "share_name": share,
    #             "share_price": share_price,
    #         "Money Control": all_screener_data_dict[share_name]["Money Control"],
    #     }
    # )

    # prompt = ratio_prompt(all_screener_data_list)
    # model = genai.GenerativeModel("gemini-1.5-flash")
    # analysis = model.generate_content(prompt)

    # ai_data = analysis.text
    # pattern = r"""\{(?:[^{}]|(?R))*\}"""

    # matches = re.findall(pattern, ai_data, re.DOTALL)[0]
    # data = json.loads(matches)

        try:
            driver.quit()
        except:
            pass

    except NoSuchElementException:
        logging.error(f"Failed to find stock name for {share}")
        return {"unscraped_companies": share}


    except SQLAlchemyError as db_error:
        session.rollback()
        logging.error(f"Database error: {str(db_error)}")
        return {"error": "Database update failed", "details": str(db_error)}

    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return {"error": "An unexpected error occurred", "details": str(e)}
    finally:
        session.close() 


# if __name__ == "__main__" :
#     # ration("AARON")
