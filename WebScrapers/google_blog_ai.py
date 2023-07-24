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
def scrapeGoogleBlogAI(targetNumWeek):
    print('Starting scraping Google Blog AI...')
    pageUrl = 'https://www.blog.google/technology/ai/'
    isWithinSearchWeek = True
    driver = webdriver.Chrome(options=create_option())
    driver.get(pageUrl)
    blogs_list = []

    while (isWithinSearchWeek):
        # Wait until all blogs are presented on the web
        try:
            articles = WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'nav.article-list__feed div.feed-article')))
        except TimeoutException:
            print('Loading take too long')
            break
        # print(articles)
        last_article_date = articles[-1].find_element(By.CSS_SELECTOR, 'time.uni-timesince').get_attribute('datetime')
        last_article_date = datetime.strptime(last_article_date.split(' ')[0], '%Y-%m-%d')

        # Check for the last post's published date, if within the target week, keep loading more contents
        if (datetime.now() - last_article_date) > timedelta(weeks=targetNumWeek):
            for article in articles:
                title = article.find_element(By.CSS_SELECTOR, 'h3.feed-article__title').text
                date = article.find_element(By.CSS_SELECTOR, 'time.uni-timesince').get_attribute('datetime')
                date = datetime.strptime(date.split(' ')[0], '%Y-%m-%d')
                link = article.find_element(By.CSS_SELECTOR, 'div.feed-article > a').get_attribute('href')
                if (datetime.now() - date) > timedelta(weeks=targetNumWeek):
                    isWithinSearchWeek = False
                    break
                blogs_list.append([date.strftime(outputDateFormat), title, link])
            break

        # Load more stories
        load_more_btn = driver.find_element(By.CSS_SELECTOR, 'button.article-list__load-more--cards')
        load_more_btn.send_keys(Keys.ENTER)

    # Write data into file
    writeScrapedData('Google Blog AI', fileName, blogs_list, targetNumWeek)
    print('Scraping Google Blog AI Finished')
    driver.quit()
