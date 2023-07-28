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
def scrapeHuggingFace(targetNumWeek):
    web_name = 'Hugging Face'
    print(f'Starting scraping {web_name}...')
    pageUrl = 'https://huggingface.co/blog'
    isWithinSearchWeek = True
    driver = webdriver.Chrome(options=create_option(headless=False))
    driver.get(pageUrl)
    blogs_list = []

    while (isWithinSearchWeek):
        # Wait until all blogs are presented on the web
        try:
            blogs = WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'main > div:nth-child(1) > div:nth-child(1) > div:nth-child(3) > a')))
        except TimeoutException:
            print('Loading take too long')
            break

        for blog in blogs:
            title = blog.find_element(By.CSS_SELECTOR, 'div:nth-child(2) > h2').get_attribute('textContent').replace('\n', '').strip()
            date = datetime.strptime(blog.find_element(By.CSS_SELECTOR, 'div:nth-child(2) > p span:nth-child(3)').get_attribute('textContent'), '%B %d, %Y')
            link = blog.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')
            if (datetime.now() - date) > timedelta(weeks=targetNumWeek):
                isWithinSearchWeek = False
                break
            if ([date.strftime(outputDateFormat), title, link] in blogs_list):
                continue
            blogs_list.append([date.strftime(outputDateFormat), title, link])

        try:
            next_page_btn = driver.find_element(By.CSS_SELECTOR, 'main > div:nth-child(1) > div:nth-child(1) > nav:nth-of-type(1) ul li:last-child > a')
            next_page_btn.send_keys(Keys.ENTER)
        except Exception:
            break

    # Write data into file
    writeScrapedData(web_name, fileName, blogs_list, targetNumWeek)
    print(f'Scraping {web_name} Finished')
    driver.quit()
