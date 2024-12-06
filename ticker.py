import json
import os
import time
import random
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait


def filter_data(html):
    soup = BeautifulSoup(html, "html.parser")

    # Extract table headers
    headers = [header.text.strip() for header in soup.select("thead th")]

    # Extract table rows
    result = []
    for row in soup.select("tbody tr"):
        cells = row.find_all(["th", "td"])
        row_data = [cell.get_text(strip=True) for cell in cells]
        result.append(dict(zip(headers, row_data)))

    return result


def ticker(company):
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
    driver.get(f"https://ticker.finology.in/company/{company}")

    all_ticker_details_list = []
    all_ticker_details_dict = {}

    try:
        share_name = driver.find_element(By.XPATH, "//span[@class='h1 font-weight-bold']").text
        all_ticker_details_dict["Share Name"] = share_name
    except:
        all_ticker_details_dict["Share Name"] = ""

    week_high = driver.find_element(By.XPATH, "//span[@id='mainContent_ltrl52WH']").text
    all_ticker_details_dict["52 Week High"] = week_high

    week_low = driver.find_element(By.XPATH, "//span[@id='mainContent_ltrl52WL']").text
    all_ticker_details_dict["52 Week Low"] = week_low

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

        # Add the extracted data to the dictionary
        if label_text and number_value:
            data[label_text] = number_value

    company_essentials_detail.append(data)

    all_ticker_details_dict["Company Essentials"] = company_essentials_detail

    # ---------------------- pledging --------------------------------
    time.sleep(5)
    try:
        pledging_html = driver.find_element(
            By.XPATH,
            "//table[@class='table table-sm table-hover screenertable  table-responsive-sm texttable']",
        ).get_attribute("outerHTML")
        soup = BeautifulSoup(pledging_html, "html.parser")

        # Find the table
        table = soup.find("table", class_="screenertable")

        # Extract "Pledge %" data
        pledge_data = []
        rows = table.find("tbody").find_all("tr")  # Find all rows in the table body
        pledge_data_dict = {}
        for row in rows:
            cells = row.find_all("td")
            date = cells[0].text.strip()
            pledge_percentage = cells[
                2
            ].text.strip()  # Get the "Pledge %" column (3rd column)
            pledge_data_dict.update({date: pledge_percentage})
        pledge_data.append(pledge_data_dict)

        all_ticker_details_dict["Pledging"] = pledge_data
    except:
        all_ticker_details_dict["Pledging"] = []
    # ------------------------------------------------------------
    strengths_details = []

    for strengths in driver.find_elements(
        By.XPATH, "//div[@class='scrollablebox ps']//ul[@class='strength']//li"
    ):
        strengths_details.append(strengths.text)

    all_ticker_details_dict["Strengths"] = strengths_details

    time.sleep(random.randint(1, 10))
    limitations_details = []
    for limitations in driver.find_elements(
        By.XPATH, "//div[@class='scrollablebox ps']//ul[@class='limitations']//li"
    ):
        limitations_details.append(limitations.text)

    all_ticker_details_dict["Limitations"] = limitations_details

    time.sleep(random.randint(1, 10))
    # quarterly result
    quarterly_table = driver.find_element(
        By.XPATH, "//div[@id='mainContent_quarterly']//table"
    ).get_attribute("outerHTML")

    # Extract table rows
    quarterly_result = filter_data(quarterly_table)

    all_ticker_details_dict["Quarterly Result"] = quarterly_result

    time.sleep(random.randint(1, 10))
    # profit_result
    profit_table = driver.find_element(
        By.XPATH, "//div[@id='profit']//table"
    ).get_attribute("outerHTML")

    # Extract table rows
    profit_result = filter_data(profit_table)

    all_ticker_details_dict["Profit & Loss"] = profit_result

    time.sleep(random.randint(1, 10))
    # Balance_result
    balance_table = driver.find_element(
        By.XPATH, "//div[@id='balance']//table"
    ).get_attribute("outerHTML")

    soup = BeautifulSoup(balance_table, "html.parser")

    # Extract table headers
    headers = [header.text.strip() for header in soup.select("thead th")]

    # Extract table rows and organize into categories
    equity_and_liabilities = []
    assets = []
    current_category = None

    for row in soup.select("tbody tr"):
        # Check for category rows
        category_cell = row.find("th")
        if (
            category_cell
            and "scope" in category_cell.attrs
            and category_cell["scope"] == "row"
        ):
            category_text = category_cell.text.strip()
            if category_text in ["Equity and Liabilities", "Assets"]:
                current_category = category_text
                continue

        # Process rows under the current category
        if current_category:
            cells = row.find_all(["th", "td"])
            row_data = [cell.get_text(strip=True) for cell in cells]
            if len(row_data) == len(headers):  # Ensure data integrity
                data_entry = dict(zip(headers, row_data))
                if current_category == "Equity and Liabilities":
                    equity_and_liabilities.append(data_entry)
                elif current_category == "Assets":
                    assets.append(data_entry)

    # Organize the final output
    Balance_result = [
        {"Equity and Liabilities": equity_and_liabilities, "Assets": assets}
    ]

    all_ticker_details_dict["Balance Sheet"] = Balance_result

    time.sleep(random.randint(1, 10))
    # cash flow
    driver.refresh()
    try:
        cash_table = driver.find_element(By.XPATH, "//div[@id='mainContent_cashflows']//table").get_attribute("outerHTML")
    except:
        cash_table = None
    if cash_table is not None:
        cash_result = filter_data(cash_table)

        all_ticker_details_dict["Cash Flows"] = cash_result

    all_ticker_details_list.append(all_ticker_details_dict)

    return all_ticker_details_list

    # with open(f"ticker_details/{company}.json", "w", encoding="utf-8") as f:
    #     json.dump(all_ticker_details_list, f, indent=4)
