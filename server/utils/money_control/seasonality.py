import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options


def seasonality(share):
    print("seasonality")
    # remote_url = "https://aazikodevai:NZwemA9rQcjbGpVV34OFHBzjLkKklAcmj65wEVNA8s2x7tJMpd@hub.lambdatest.com/wd/hub"
    remote_url = "https://ronak285.rejoice:cWTZL7vA7zeDoGkLEFOMGCMIg10ZNlYn5wYhWNScOTXsxoO70B@hub.lambdatest.com/wd/hub"
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
    time.sleep(random.randint(1, 10))

    search = driver.find_element(By.XPATH, "//textarea[@class='gLFyf']")
    search.send_keys(f"{share} money control")
    time.sleep(random.randint(1, 10))
    search.send_keys(Keys.ENTER)

    time.sleep(random.randint(1, 10))
    driver.find_element(By.XPATH, "//div[@class='yuRUbf']//div//span//a").click()

    driver.refresh()

    time.sleep(random.randint(1, 10))

    driver.execute_script("window.scrollTo(0, 0);")

    seasonality_analysis_link = driver.find_element(
        By.XPATH,
        "//div[@id='SeasonalityAnalysis']//div[@class='showMoreBtnWrap']//a[@href]",
    ).get_attribute("href")
    driver.get(seasonality_analysis_link)

    seasonality_analysis = []
    for seasonality_analysis_table_index in driver.find_elements(
        By.XPATH,
        "//div[@class='seasonality_web_SeasonalityTable__DzLh7']//table//thead//tr",
    ):
        row_data = [
            th.text
            for th in seasonality_analysis_table_index.find_elements(By.TAG_NAME, "th")
        ]

        if row_data == []:
            continue
        seasonality_analysis.append(row_data)

    for seasonality_analysis_table_value in driver.find_elements(
        By.XPATH,
        "//div[@class='seasonality_web_SeasonalityTable__DzLh7']//table//tbody//tr",
    ):
        row_data = [
            th.text
            for th in seasonality_analysis_table_value.find_elements(By.TAG_NAME, "td")
        ]

        if row_data == []:
            continue
        seasonality_analysis.append(row_data)

    seasonality_analysis_headers = seasonality_analysis[0]
    seasonality_analysis_json_data = [
        dict(zip(seasonality_analysis_headers, row)) for row in seasonality_analysis[1:]
    ]

    driver.quit()
    print("collecting seasonality data")

    return seasonality_analysis_json_data
