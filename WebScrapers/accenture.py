import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from datetime import datetime, timedelta
from Utils.error_handler import handle_scrape_errors
from Utils.driver_options import create_option
from Utils.write_to_list import writeScrapedData
from globals import fileName, outputDateFormat


# @handle_scrape_errors
def scrapeAccenture(targetNumWeek):
    web_name = 'Accenture'
    print(f'Starting scraping {web_name}...')
    pageUrls = ['https://www.accenture.com/us-en/blogs/high-tech',
                'https://www.accenture.com/us-en/blogs/cloud-computing',
                'https://www.accenture.com/us-en/blogs/software-engineering-blog']
    driver = webdriver.Chrome(options=create_option(headless=False))
    blogs_list = []

    def scrapeSection(url):
        print(f'working on: {url}')
        driver.get(url)

        def getFeaturedPost():
            # Wait until featured post is presented on the web
            try:
                post = WebDriverWait(driver, 8).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#blog-featured-post')))
            except TimeoutException:
                print('Featured post not avaiable')
                return

            title = post.find_element(By.CSS_SELECTOR, 'div.featured-headline').get_attribute('textContent').replace('\n', '').strip()
            date = post.find_element(By.CSS_SELECTOR, 'div.featured-details-cont.small.corporate-semibold.ucase span.featured-date').get_attribute('textContent')
            date = datetime.strptime(date, '%B %d, %Y')
            link = post.find_element(By.CSS_SELECTOR, 'div.featured-cta.corporate-semibold > a').get_attribute('href')
            if (datetime.now() - date) > timedelta(weeks=targetNumWeek):
                return
            blogs_list.append([date.strftime(outputDateFormat), title, link])

        def getMorePosts():
            # Wait until all posts are presented on the web
            try:
                posts = WebDriverWait(driver, 8).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '#block-sectionpagezonetwocolumn > div > div > div:nth-child(1) > div.col-lg-4.col-md-4.col-sm-12.col-xs-12 > div > div.blog-more-posts-cards-container.col-sm-12.col-xs-12 > a')))
            except TimeoutException:
                print('More posts not avaiable')
                return

            for post in posts:
                title = post.find_element(By.CSS_SELECTOR, 'article > div.col-xs-8 > div > div.blog-more-posts-cards-title > span').get_attribute('textContent').replace('\n', '').strip()
                date = post.find_element(By.CSS_SELECTOR, 'article > div.col-xs-8 > div > div.blog-more-posts-cards-date').get_attribute('textContent').replace('\n', '').strip()
                date = datetime.strptime(date, '%B %d, %Y')
                link = post.get_attribute('href')
                if (datetime.now() - date) > timedelta(weeks=targetNumWeek):
                    break
                if ([date.strftime(outputDateFormat), title, link] in blogs_list):
                    continue
                blogs_list.append([date.strftime(outputDateFormat), title, link])

        def getRecentPosts():
            # Wait until all posts are presented on the web
            try:
                posts = WebDriverWait(driver, 8).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '#block-recent-posts > div > div.block-content.col-lg-12.col-md-12.col-sm-12.col-xs-12 > div > div > div:not(:last-child) > a')))
            except TimeoutException:
                print('Recent posts not avaiable')
                return

            for post in posts:
                title = post.find_element(By.CSS_SELECTOR, 'div.blog-content-container > div > h3').get_attribute('textContent').replace('\n', '').strip()
                date = post.find_element(By.CSS_SELECTOR, 'div.blog-content-container > div > span').get_attribute('textContent').replace('\n', '').strip()
                date = datetime.strptime(date, '%B %d, %Y')
                link = post.get_attribute('href')
                if (datetime.now() - date) > timedelta(weeks=targetNumWeek):
                    break
                if ([date.strftime(outputDateFormat), title, link] in blogs_list):
                    continue
                blogs_list.append([date.strftime(outputDateFormat), title, link])

        getFeaturedPost()
        getMorePosts()
        getRecentPosts()

    for url in pageUrls:
        scrapeSection(url)

    # Write data into file
    writeScrapedData(web_name, fileName, blogs_list, targetNumWeek)
    print(f'Scraping {web_name} Finished')
    driver.quit()
