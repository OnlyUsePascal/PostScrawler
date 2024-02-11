from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from datetime import datetime, timedelta
from Utils.error_handler import handle_scrape_errors
from Utils.driver_options import create_option
from Utils.write_to_list import writeMessage, writeScrapedData
from globals import fileName, outputDateFormat
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time


@handle_scrape_errors
def scrapeAcademyBinance(targetNumWeek):
    print('---> Academy Binance')
    pageUrl = 'https://academy.binance.com/en/articles?page=1'
    print(f'> {pageUrl}')
    # writeMessage(fileName, f'> {pageUrl}')
    delay = 1
    isWithinSearchWeek = True
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(options=create_option(headless=True), service=service)
    # driver = webdriver.Chrome(options=create_option())
    driver.get(pageUrl)
    blogs_list = []

    # Clear the filter bc there are bugs where the website open up with filter sometimes
    clear_filter_btn = driver.find_element(By.CSS_SELECTOR, 'button.css-1nkwl0a')
    clear_filter_btn.send_keys(Keys.ENTER)
    # Choose the list style cuz there are bugs with grid style
    list_layout_btn = driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Switch results to list layout"]')
    list_layout_btn.send_keys(Keys.ENTER)

    while (isWithinSearchWeek):
        blogs_title = driver.find_elements(By.CSS_SELECTOR, 'div.css-8qb8m4 h3.css-1ctqeuv')
        blogs_date = driver.find_elements(By.CSS_SELECTOR, 'div.css-fv3lde span.css-1sj28o2')
        blogs_link = driver.find_elements(By.CSS_SELECTOR, 'div.css-8qb8m4 > a')

        for i in range(len(blogs_title)):
            if (datetime.now() - datetime.strptime(blogs_date[i].text, '%b %d, %Y')) > timedelta(weeks=targetNumWeek):
                isWithinSearchWeek = False
                break
            date = datetime.strptime(blogs_date[i].text, '%b %d, %Y')
            blogs_list.append([date.strftime(outputDateFormat), blogs_title[i].get_attribute('title'), blogs_link[i].get_attribute('href')])

        # Go to next page
        print('+ still searching')
        next_page_btn = driver.find_element(By.CSS_SELECTOR, 'a[aria-label="Go to next page"]')
        next_page_btn.send_keys(Keys.ENTER)
        time.sleep(delay)

    # Write data into file
    writeScrapedData('Academy Binance', fileName, blogs_list, targetNumWeek, pageUrl)
    print('> Done\n')
    driver.quit()
