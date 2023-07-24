from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from datetime import datetime, timedelta
from Utils.error_handler import handle_scrape_errors
from Utils.driver_options import create_option
from Utils.write_to_list import writeScrapedData
from globals import fileName, outputDateFormat


@handle_scrape_errors
def scrapeOpenAI(targetNumWeek):
    print('Starting scraping OpenAI...')
    pageUrl = 'https://openai.com/blog'
    isWithinSearchWeek = True
    driver = webdriver.Chrome(options=create_option())
    driver.get(pageUrl)
    blogs_list = []

    while (isWithinSearchWeek):
        # Wait until all blogs are presented on the web
        try:
            blogs = WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.ui-list ul.cols-container li')))
        except TimeoutException:
            print('Loading take too long')
            break
        for blog in blogs:
            title = blog.find_element(By.CSS_SELECTOR, 'div h3').text
            date = datetime.strptime(blog.find_element(By.CSS_SELECTOR, 'div span[aria-hidden="true"]').text, '%b %d, %Y')
            link = blog.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')
            if (datetime.now() - date) > timedelta(weeks=targetNumWeek):
                isWithinSearchWeek = False
                break
            blogs_list.append([date.strftime(outputDateFormat), title, link])

        next_page_btn = driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Next page"]')
        next_page_btn.send_keys(Keys.ENTER)

    # Write data into file

    writeScrapedData('OpenAI', fileName, blogs_list, targetNumWeek)
    print('Scraping OpenAI Finished')
    driver.quit()
