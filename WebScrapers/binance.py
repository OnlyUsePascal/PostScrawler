import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from datetime import datetime, timedelta
from Utils.error_handler import handle_scrape_errors
from Utils.driver_options import create_option
from Utils.write_to_list import writeFileTitle, writeFileData, writeScrapedData
from globals import fileName, outputDateFormat

# @handle_scrape_errors
def scrapeBinance(targetNumWeek):
    web_name = 'Binance'
    print(f'Starting scraping {web_name}...')
    writeFileTitle(f'=== {web_name} ===')

    pageUrls = ['https://www.binance.com/en/research/analysis ',
                'https://www.binance.com/en/research/projects']
    driver = webdriver.Chrome(options=create_option())

    def scrapeSection(url):
        print(f'working on: {url}')
        writeFileTitle(f'> {url}')
        blogs_list = []

        driver.get(url)

        # Wait until featured post is presented on the web
        time.sleep(6)
        try:
            posts = WebDriverWait(driver, 8).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.sc-5d4f8ada-0 > a')))
        except TimeoutException:
            print('Post not avaiable')
            return

        for post in posts:
            title = post.find_element(By.CSS_SELECTOR, 'div:nth-child(2) > div:nth-child(1) > div:nth-child(1)').get_attribute('textContent').replace('\n', '').strip()

            date = post.find_element(By.CSS_SELECTOR, 'div:nth-child(2) > div:nth-child(2)').get_attribute('textContent')
            date = datetime.strptime(date, '%Y-%m-%d')

            link = post.get_attribute('href')
            if (datetime.now() - date) > timedelta(weeks=targetNumWeek):
                continue
            blogs_list.append([date.strftime(outputDateFormat), title, link])

        writeFileData(blogs_list, targetNumWeek)

    for url in pageUrls:
        scrapeSection(url)

    # Write data into file
    print(f'Scraping {web_name} Finished')
    driver.quit()
