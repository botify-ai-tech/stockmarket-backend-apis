import gc
import json
import time
import random
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait

from fastapi import APIRouter
from server.utils.money_control.other_ratios import (
    additional_ratios,
    calculate_cash_flow_to_sales_ratio,
    efficiency_ratios,
    market_valuation_ratios,
    other_ratios,
    profitability_ratios,
    risk_and_solvency_ratios,
)
from server.utils.money_control.scan import scans
from server.utils.money_control.ratio import ratio
from server.utils.money_control.seasonality import seasonality
from server.schemas.ratio import RatioBase


ratio_router = APIRouter()


@ratio_router.post("/ratio")
def money_con_ration(share: RatioBase):
    remote_url = "https://darshan184.rejoice:RBJITAq3ocVXX23KABUqLeBO8HSWMd3nUqFE8XlFd27qdDibu1@hub.lambdatest.com/wd/hub"

    chrome_options = Options()
    chrome_options.browser_version = "latest"
    chrome_options.platform_name = "Windows 10"
    chrome_options.set_capability("build", "scraping-lambdatest")
    chrome_options.set_capability("name", "scraping-test")
    chrome_options.set_capability("visual", True)
    chrome_options.set_capability("console", False)
    chrome_options.set_capability("network", False)

    # Initialize the remote WebDriver
    driver = webdriver.Remote(command_executor=remote_url, options=chrome_options)
    driver.get("https://www.screener.in/")

    all_screener_data_list = []
    all_screener_data_dict = {}

    # time.sleep(random.randint(1, 10))
    driver.refresh()
    # time.sleep(random.randint(1, 10))
    # with open("all_share.txt", "r") as f:
    #     all_share = f.readlines()
    # lines = [line.strip() for line in lines]

    # # Shuffle the list to randomize the order
    # random.shuffle(lines)
    # for share in lines:
    # try:
    search_wait = WebDriverWait(driver, 10)
    search_wait.until(
        lambda driver: driver.find_element(
            By.XPATH, "//div[@class='home-search']//input[@class='u-full-width']"
        )
    )
    search = driver.find_element(
        By.XPATH, "//div[@class='home-search']//input[@class='u-full-width']"
    )
    search.send_keys(share)
    # time.sleep(random.randint(1, 10))
    print("=============")
    search.send_keys(Keys.ENTER)
    # except:
    #     pass

    try:
        search = driver.find_element(
            By.XPATH, "//div[@class='search']//input[@class='u-full-width']"
        )
        search.send_keys(share)
        # time.sleep(random.randint(1, 10))
        search.send_keys(Keys.ENTER)
    except:
        pass

    # ------------------------------------------------------------ Share details ------------------------------------------------------------
    print("Share details")
    # time.sleep(random.randint(1, 10))
    # Share Name
    share_name = driver.find_element(
        By.XPATH, "//div[@class='card card-large']//div//div//h1"
    ).text

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
    print("Chart")

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

    # ------------------------------------------------------------ Analysis ------------------------------------------------------------
    print("Analysis")

    pros = driver.find_element(By.XPATH, "//section[@id='analysis']//div//div//ul").text

    cons = driver.find_element(
        By.XPATH, "//section[@id='analysis']//div//div[@class='cons']//ul"
    ).text

    all_screener_data_dict[share_name]["Screener"]["analysis"] = {
        "pros": pros,
        "cons": cons,
    }
    # ----------------------------------------------------------- Expanded view -----------------------------------------------------------
    print("Expanded view")
    for button in driver.find_elements(
        By.XPATH,
        "//table[@class='data-table responsive-text-nowrap']//tbody//tr//td//button",
    ):
        button.click()

    # ------------------------------------------------------------ Peer comparison ------------------------------------------------------------
    print("Peer comparison")

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

    # ------------------------------------------------------------ Quarterly Results ------------------------------------------------------------
    print("Quarterly Results")

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
    print("Profit & Loss")

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

    profit_loss_other_table = []
    for profit_loss_table_other_index in driver.find_elements(
        By.XPATH,
        "//section[@id='profit-loss']//div[4]//table[@class='ranges-table']//tbody//tr",
    ):
        profit_loss_other_table.append(profit_loss_table_other_index.text)

    structured_data = {}

    # Helper function to extract the periods and values
    def extract_period_values(values):
        return {period.split(": ")[0]: period.split(": ")[1] for period in values}

    # Iterate over the data_list and structure the data
    i = 0
    while i < len(profit_loss_other_table):
        key = profit_loss_other_table[i]
        values = []
        i += 1
        while i < len(profit_loss_other_table) and ":" in profit_loss_other_table[i]:
            values.append(profit_loss_other_table[i])
            i += 1
        structured_data[key] = extract_period_values(values)

    profit_loss_headers = profit_loss[0]

    # Convert list of lists to list of dictionaries
    profit_loss_json_data = [
        dict(zip(profit_loss_headers, row)) for row in profit_loss[1:]
    ]

    profit_loss_json_data.append(structured_data)

    all_screener_data_dict[share_name]["Screener"][
        "Profit & Loss"
    ] = profit_loss_json_data

    # ------------------------------------------------------------- Balance Sheet -------------------------------------------------------------
    print("Balance Sheet")

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
    print("Cash Flows")

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
    print("Ratios")

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
    print("Shareholding Pattern")

    # ===================== Quarterly =====================
    shareholding_pattern_quarterly = []
    shareholding_pattern_dict = {}
    shareholding_pattern_dict["Quarterly"] = {}
    shareholding_pattern_dict["Yearly"] = {}

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

    all_screener_data_dict[share_name]["Screener"][
        "Shareholding Pattern"
    ] = shareholding_pattern_dict

    # -------------------------------------------------------------- Documents -------------------------------------------------------------
    print("Documents")
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
    print("annual reports")
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

    all_screener_data_dict[share_name]["Screener"]["Documents"] = documents_dict

    # all_screener_data_list.append(all_screener_data_dict)
    # -------------------------------------------------------------------------- Money Control -------------------------------------------------------------
    all_screener_data_dict[share_name]["Money Control"] = {}
    try:
        print("Money Control")
        driver.get("https://www.google.com/")
        time.sleep(1)
        driver.refresh()
        # time.sleep(random.randint(1, 10))

        search = driver.find_element(By.XPATH, "//textarea[@class='gLFyf']")
        time.sleep(1)
        search.send_keys(f"{share} money control")
        # time.sleep(random.randint(1, 10))
        search.send_keys(Keys.ENTER)

        # time.sleep(random.randint(1, 10))
        driver.refresh()
        driver.find_element(By.XPATH, "//div[@class='yuRUbf']//div//span//a").click()

        sector_pe = driver.find_element(
            By.XPATH,
            "//div[@class='overview_section']//div[@class='clearfix']//div[@class='mob-hide']//div[@class='oview_table']//table//tbody//tr//td[@class='nsesc_ttm bsesc_ttm']",
        ).text
        print("sector_pe", sector_pe)

        all_screener_data_dict[share_name]["Money Control"]["Sector PE"] = sector_pe

    except Exception as e:
        print(e)
        pass

    # ----------------------------------------------------------- About the Company --------------------------------------------
    print("About the Company")

    driver.refresh()
    # time.sleep(random.randint(1, 10))

    about_wait = WebDriverWait(driver, 10)
    about_wait.until(
        lambda driver: driver.find_element(
            By.XPATH, "//div[@id='company_info']//ul[@class='comp_inf company_slider']"
        )
    )

    about = driver.find_element(
        By.XPATH, "//div[@id='company_info']//ul[@class='comp_inf company_slider']"
    )
    about_html = about.get_attribute("outerHTML")

    soup = BeautifulSoup(about_html, "html.parser")
    data = {}
    section_headers = soup.find_all("h3", class_="all_title_inner com_brdb")

    for header in section_headers:
        section_title = header.get_text(strip=True)
        section_list = []

        # Find the next sibling <ul> that contains the details
        ul = header.find_next_sibling("ul")
        if ul:
            for li in ul.find_all("li"):
                key = li.find("span").get_text(strip=True)
                value = li.find("p").get_text(strip=True)
                section_list.append({key: value})

        data[section_title] = section_list

    all_screener_data_dict[share_name]["Money Control"]["About the Company"] = data

    driver.quit()
    gc.collect()
    gc.collect()
    # time.sleep(random.randint(1, 10))

    # ---------------------------------------------------------- SCANS ------------------------------------------------------------

    # scan_response = scans(share)
    # scan_detail = scan_response.get("scans")
    # ratio_response = scan_response.get("ratios")

    # all_screener_data_dict[share_name]["Money Control"]["SCANS"] = scan_detail

    # ---------------------------------------------------- SEASONALITY ANALYSIS -------------------------------------------------------

    # seasonality_analysis_json_data = seasonality(share)

    # all_screener_data_dict[share_name]["Money Control"][
    #     "SEASONALITY ANALYSIS"
    # ] = seasonality_analysis_json_data

    # ----------------------------------------------------------- Ratios ------------------------------------------------------------

    ratio_response = ratio(share)

    ration_data = ratio_response.get("Ratios")

    all_screener_data_dict[share_name]["Money Control"]["Ratios"] = ration_data

    # -------------------------------------------------------------- Cash Flow Ratio -------------------------------------------------------------------
    print("Cash Flow Ratio")
    operating_cash_flow_to_sales_ratio = calculate_cash_flow_to_sales_ratio(
        all_screener_data_dict, share_name
    )
    operating_cash_flow_to_sales_ratio = operating_cash_flow_to_sales_ratio.get(
        "Cash Flow Ratios"
    )

    all_screener_data_dict[share_name]["Money Control"][
        "Cash Flow Ratios"
    ] = operating_cash_flow_to_sales_ratio

    # -------------------------------------------------------------- Efficiency Ratio -------------------------------------------------------------------
    print("Efficiency Ratio")
    efficiency_ratio = efficiency_ratios(all_screener_data_dict, share_name)
    efficiency_ratio = efficiency_ratio.get("Efficiency Ratios")
    all_screener_data_dict[share_name]["Money Control"][
        "Efficiency Ratios"
    ] = efficiency_ratio

    # ------------------------------------------------------------- Profitability Ratios -------------------------------------------------------------
    print("Profitability Ratios")
    profitability_ratio = profitability_ratios(all_screener_data_dict, share_name)
    profitability_ratio = profitability_ratio.get("Profitability Ratios")
    all_screener_data_dict[share_name]["Money Control"][
        "Profitability Ratios"
    ] = profitability_ratio

    # -------------------------------------------------------- Market Valuation Ratios --------------------------------------------------------
    print("Market Valuation Ratios")
    market_valuation_ratio = market_valuation_ratios(all_screener_data_dict, share_name)
    market_valuation_ratio = market_valuation_ratio.get("Market Valuation Ratios")

    all_screener_data_dict[share_name]["Money Control"][
        "Market Valuation Ratios"
    ] = market_valuation_ratio

    #  ------------------------------------------------------ Additional Ratios --------------------------------------------------
    print("Additional Ratios")
    additional_ratio_details = additional_ratios(all_screener_data_dict, share_name)
    additional_data = additional_ratio_details.get("Additional Ratios")

    all_screener_data_dict[share_name]["Money Control"][
        "Additional Ratios"
    ] = additional_data

    # ------------------------------------------------------ Other rations --------------------------------------------------
    print("Other rations")
    other_ratios_details = other_ratios(all_screener_data_dict, share_name)
    other_ratios_data = other_ratios_details.get("Other Ratios")

    all_screener_data_dict[share_name]["Money Control"][
        "Other Ratios"
    ] = other_ratios_data

    # ----------------------------------------------------- Risk and Solvency Ratios -----------------------------------------------------
    print("Risk and Solvency Ratios")
    risk_and_solvency_ratios_details = risk_and_solvency_ratios(
        all_screener_data_dict, share_name
    )
    risk_and_solvency_ratios_data = risk_and_solvency_ratios_details.get(
        "Risk and Solvency Ratios"
    )

    all_screener_data_dict[share_name]["Money Control"][
        "Risk and Solvency Ratios"
    ] = risk_and_solvency_ratios_data

    # ------------------------------------------------------- Save the data -------------------------------------------------------

    all_screener_data_list.append(all_screener_data_dict)

    print("Collect all the data")

    file_path = f"all_screener_data//{share}.json"
    with open(file_path, "w", encoding="iso-8859-1") as f:
        json.dump(all_screener_data_list, f, indent=4)

    try:
        driver.quit()
    except:
        pass

    return all_screener_data_list
