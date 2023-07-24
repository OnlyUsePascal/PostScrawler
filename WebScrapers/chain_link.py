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
def scrapeChainlink(targetNumWeek):
    print('Starting scraping Chainlink...')
    pageUrl = 'https://blog.chain.link/'
    isWithinSearchWeek = True
    driver = webdriver.Chrome(options=create_option(page_load_strategy='none'))
    driver.get(pageUrl)
    blogs_list = []

    while (isWithinSearchWeek):
        # Wait until all blogs are presented on the web
        try:
            post_cards = WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.blog-post-bar div.post-card')))
        except TimeoutException:
            print('Loading take too long')
            break
        last_post_date = post_cards[-1].find_element(By.CSS_SELECTOR, 'span.post-date').text
        last_post_date = datetime.strptime(last_post_date, '%B %d, %Y')

        # Check for the last post's published date, if within the target week, keep loading more contents
        # else, start scraping contents
        if (datetime.now() - last_post_date) > timedelta(weeks=targetNumWeek):
            for post in post_cards:
                title = post.find_element(By.CSS_SELECTOR, 'div.post-title a').text
                date = datetime.strptime(post.find_element(By.CSS_SELECTOR, 'span.post-date').text, '%B %d, %Y')
                link = post.find_element(By.CSS_SELECTOR, 'div.post-title a').get_attribute('href')
                if (datetime.now() - date) > timedelta(weeks=targetNumWeek):
                    isWithinSearchWeek = False
                    break
                blogs_list.append([date.strftime(outputDateFormat), title, link])
            break

        # Load more contents
        load_more_btn = driver.find_element(By.CSS_SELECTOR, 'a.loadmore-btn')
        load_more_btn.send_keys(Keys.ENTER)

    # Write data into file
    writeScrapedData('Chainlink', fileName, blogs_list, targetNumWeek)
    print('Scraping Chainlink Finished')
    driver.quit()
