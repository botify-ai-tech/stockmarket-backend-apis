import logging
import os
import time
import random
import requests
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

from dotenv import load_dotenv

load_dotenv()


def ratio(share):
    logging.info("RATIO")

    remote_url = os.getenv("LAMBDA_CHROME_URL")

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

    driver.get("https://www.google.com/")
    # time.sleep(random.randint(100, 120))
    search = driver.find_element(By.XPATH, "//textarea[@class='gLFyf']")
    search.send_keys(f"{share} money control")
    # time.sleep(random.randint(1, 10))
    search.send_keys(Keys.ENTER)

    time.sleep(random.randint(1, 10))
    driver.find_element(By.XPATH, "//div[@class='yuRUbf']//div//span//a").click()

    url = driver.current_url
    symbol = url.split("/")[-1]

    headers = {
        "accept": "text/html, */*; q=0.01",
        "accept-language": "en-US,en;q=0.9",
        "priority": "u=1, i",
        "referer": f"https://www.moneycontrol.com/india/stockpricequote/auto-lcvshcvs/tatamotors/{symbol}",
        "sec-ch-ua": '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
    }

    params = {
        "classic": "true",
        "referenceId": "ratios",
        "scId": f"{symbol}",
        "requestType": "S",
        "frequency": "",
    }

    response = requests.get(
        "https://www.moneycontrol.com/mc/widget/mcfinancials/getFinancialData",
        params=params,
        headers=headers,
    )
    time.sleep(random.randint(1, 10))

    ratio_html = response.content

    soup = BeautifulSoup(ratio_html, "html.parser")

    # This dictionary will store all the ratios in the required format
    data = {
        "Ratios": {
            "Per Share Ratios": [],
            "Margin Ratios": [],
            "Return Ratios": [],
            "Liquidity Ratios": [],
            "Leverage Ratios": [],
            "Turnover Ratios": [],
            "Growth Ratios": [],
            "Valuation Ratios": [],
        }
    }

    # Assuming each category of ratios is in a div or table with a unique identifier
    # You might need to adjust the selectors based on actual HTML structure
    for category in data["Ratios"].keys():
        # Find the section containing the category of ratios
        section = soup.find("div", id=f"C_{category.lower().replace(' ', '_')}")
        if section is None:
            section = soup.find("div", id=f"S_{category.lower().replace(' ', '_')}")

        if not section:
            continue

        # Extract the rows of ratios within this section
        for row in section.find_all("tr")[1:]:  # Skipping the header row
            cells = row.find_all("td")
            if not cells:
                continue

            ratio_data = {
                "Ratio": cells[0].text.strip(),
                "Mar 2024": cells[1].text.strip(),
                "Mar 2023": cells[2].text.strip(),
                "Mar 2022": cells[3].text.strip(),
                "Mar 2021": cells[4].text.strip(),
                "Mar 2020": cells[5].text.strip(),
                "Trend Mar 20 - Mar 24": (
                    cells[6].text.strip() if len(cells) > 6 else ""
                ),
            }
            data["Ratios"][category].append(ratio_data)

    driver.quit()
    logging.info("collecting ratio data")

    return data
