from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementNotInteractableException
from datetime import datetime, timedelta
import time
from Utils.error_handler import handle_scrape_errors
from Utils.driver_options import create_option
from Utils.write_to_list import writeScrapedData
from globals import fileName, outputDateFormat


@handle_scrape_errors
def scrapeVNG(targetNumWeek):
    web_name = 'VNG'
    print(f'Starting scraping {web_name}...')
    pageUrl = 'https://www.vngcloud.vn/en/blog'
    isWithinSearchWeek = True
    out_of_article = False
    driver = webdriver.Chrome(options=create_option(page_load_strategy='none'))
    blogs_list = []

    driver.get(pageUrl)
    while (isWithinSearchWeek):
        # Wait until all blogs are presented on the web
        try:
            articles = WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div#all-block div.blog-widget')))
        except TimeoutException:
            print('Loading take too long')
            break

        last_post_date = articles[-1].find_element(By.CSS_SELECTOR, 'div.blog-heading p.blog-time').get_attribute('textContent')
        last_post_date = datetime.strptime(last_post_date, '%B %d, %Y')

        # Check for the last post's published date, if within the target week, keep loading more contents
        # else, start scraping contents
        if (datetime.now() - last_post_date) > timedelta(weeks=targetNumWeek) or out_of_article:
            # Since VNG blogs are out of place, it has to be sorted base on its date
            sorted_articles = sorted(articles, key=lambda article: datetime.strptime(article.find_element(By.CSS_SELECTOR, 'div.blog-heading p.blog-time').get_attribute('textContent'), '%B %d, %Y'), reverse=True)

            for article in sorted_articles:
                title = article.find_element(By.CSS_SELECTOR, 'a.blog-title').get_attribute('textContent')
                date = datetime.strptime(article.find_element(By.CSS_SELECTOR, 'div.blog-heading p.blog-time').get_attribute('textContent'), '%B %d, %Y')
                link = article.find_element(By.CSS_SELECTOR, 'a.blog-title').get_attribute('href')
                if (datetime.now() - date) > timedelta(weeks=targetNumWeek):
                    isWithinSearchWeek = False
                    break
                blogs_list.append([date.strftime(outputDateFormat), title, link])
            break

        # Load more contents
        try:
            load_more_btn = driver.find_element(By.ID, 'latest-blog-load-more')
            load_more_btn.send_keys(Keys.ENTER)
            time.sleep(1)
        except ElementNotInteractableException:
            out_of_article = True

    # Write data into file
    writeScrapedData(web_name, fileName, blogs_list, targetNumWeek)
    print(f'Scraping {web_name} Finished')
    driver.quit()
