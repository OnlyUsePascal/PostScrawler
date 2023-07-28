import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementNotInteractableException
from datetime import datetime, timedelta
from Utils.error_handler import handle_scrape_errors
from Utils.driver_options import create_option
from Utils.write_to_list import writeScrapedData
from globals import fileName, outputDateFormat


@handle_scrape_errors
def scrapeIBM(targetNumWeek):
    web_name = 'IBM'
    print(f'Starting scraping {web_name}...')
    pageUrls = ['https://www.ibm.com/blog/category/artificial-intelligence/',
                'https://www.ibm.com/blog/category/analytics/',
                'https://www.ibm.com/blog/category/business-transformation/']
    isWithinSearchWeek = True
    driver = webdriver.Chrome(options=create_option())
    blogs_list = []

    def scrapeSection(url):
        print(f'working on: {url}')
        driver.get(url)

        while (isWithinSearchWeek):
            # Wait until all blogs are presented on the web
            # articles = driver.find_elements(By.CSS_SELECTOR, 'amp-list.amp_list div[role="list"]')
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight-200);")
            time.sleep(0.5)
            driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_UP)
            try:
                # articles = WebDriverWait(driver, 8).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div[role="list"] article.article div.article__text_container')))
                last_section_articles = WebDriverWait(driver, 8).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'amp-list.amp_list div[role="list"] article.article')))
            except TimeoutException:
                print('Loading take too long')
                break
            # Get last post's date
            last_article_date = last_section_articles[-1].find_element(By.CSS_SELECTOR, 'span.article__date').get_attribute('textContent').replace('\n', '').strip()
            last_article_date = datetime.strptime(last_article_date, '%B %d, %Y')

            # Check for the last post's published date, if within the target week, keep loading more contents
            if (datetime.now() - last_article_date) > timedelta(weeks=targetNumWeek):
                articles = driver.find_elements(By.CSS_SELECTOR, 'article.article div.article__text_container')
                for article in articles:
                    title = article.find_element(By.CSS_SELECTOR, 'h2').get_attribute('textContent').replace('\n', '').strip()
                    date = article.find_element(By.CSS_SELECTOR, 'span.article__date').get_attribute('textContent').replace('\n', '').strip()
                    date = datetime.strptime(date, '%B %d, %Y')
                    link = article.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')
                    if (datetime.now() - date) > timedelta(weeks=targetNumWeek):
                        break
                    if ([date.strftime(outputDateFormat), title, link] in blogs_list):
                        continue
                    blogs_list.append([date.strftime(outputDateFormat), title, link])
                break

            # Load more stories
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight-200);")
            tries = 5
            while tries > 0:
                try:
                    load_more_btn = driver.find_element(By.CSS_SELECTOR, 'button.btn--IBM_blog')
                    time.sleep(1)
                    load_more_btn.send_keys(Keys.ENTER)
                    break
                except ElementNotInteractableException:
                    driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_UP)
                    tries -= 1

    for url in pageUrls:
        scrapeSection(url)

    # Write data into file
    writeScrapedData(web_name, fileName, blogs_list, targetNumWeek)
    print(f'Scraping {web_name} Finished')
    driver.quit()
