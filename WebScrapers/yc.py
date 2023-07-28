from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from datetime import datetime, timedelta
# import time
from Utils.error_handler import handle_scrape_errors
from Utils.driver_options import create_option
from Utils.write_to_list import writeScrapedData
from globals import fileName, outputDateFormat


@handle_scrape_errors
def scrapeYC(targetNumWeek):
    web_name = 'Y Combinator'
    print(f'Starting scraping {web_name}...')
    pageUrls = ['https://www.ycombinator.com/blog/tag/advice?page=',
                'https://www.ycombinator.com/blog/tag/founder-stories?page=']
    driver = webdriver.Chrome(options=create_option())
    blogs_list = []

    def scrapeSection(url: str):
        print(f"Working on {url.replace('?page=', '')}")
        page = 1
        # Scrape Advices
        driver.get(url + str(page))
        try:
            advice_posts = WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'body > div:nth-child(2) > div.mx-auto.max-w-ycdc-page > section:nth-child(2) > div > div > div:nth-child(2)')))
        except TimeoutException:
            print('No advices found')
        for post in advice_posts:
            title = post.find_element(By.CSS_SELECTOR, 'div > div:nth-child(1) > a > p:nth-child(1)').get_attribute('textContent')
            date = datetime.strptime(post.find_element(By.CSS_SELECTOR, 'div > div:nth-child(3) > div:nth-child(2) > div > span').get_attribute('textContent'), '%m/%d/%Y')
            link = post.find_element(By.CSS_SELECTOR, 'div > div:nth-child(1) > a').get_attribute('href')
            if (datetime.now() - date) > timedelta(weeks=targetNumWeek):
                return
            if ([date.strftime(outputDateFormat), title, link] in blogs_list):
                continue
            blogs_list.append([date.strftime(outputDateFormat), title, link])

        # Scrape all posts
        while True:
            driver.get(url + str(page))
            # Wait until all blogs are presented on the web
            try:
                articles = WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'body > div:nth-child(2) > div.mx-auto.max-w-ycdc-page > section:nth-child(3) > div > div.col-span-2 > div > div > div')))
            except TimeoutException:
                print('No articles found')
                return
            print(len(articles))

            for post in articles:
                title = post.find_element(By.CSS_SELECTOR, 'a p').get_attribute('textContent')
                date = datetime.strptime(post.find_element(By.CSS_SELECTOR, 'p:nth-child(2) > span').get_attribute('textContent'), '%m/%d/%Y')
                link = post.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')
                if (datetime.now() - date) > timedelta(weeks=targetNumWeek):
                    return
                if ([date.strftime(outputDateFormat), title, link] in blogs_list):
                    continue
                blogs_list.append([date.strftime(outputDateFormat), title, link])

            page += 1
    
    for url in pageUrls:
        scrapeSection(url)

    # Write data into file
    writeScrapedData(web_name, fileName, blogs_list, targetNumWeek)
    print(f'Scraping {web_name} Finished')
    driver.quit()
