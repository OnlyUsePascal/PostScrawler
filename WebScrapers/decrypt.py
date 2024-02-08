import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from datetime import datetime, timedelta
from Utils.error_handler import handle_scrape_errors
from Utils.driver_options import create_option
from Utils.write_to_list import writeScrapedData, writeFileTitle, writeFileData
from Utils.SectionScrape.scrape_section import WebSection


@handle_scrape_errors
def scrapeDecrypt(targetNumWeek):
    print('Starting scraping Decrypt...')
    pageUrl = ['https://decrypt.co/news/technology',
               #'https://decrypt.co/news',
               'https://decrypt.co/deep-dives']
    driver = webdriver.Chrome(options=create_option())
    blogs_list = []
    
    delay = 2

    writeFileTitle('Decrypt')

    def scrapeSection(url):
        print(f'working on: {url}')
        driver.get(url)
        time.sleep(delay)

        # First article session
        first_blogs_list, within_week_search = \
            WebSection(driver) \
                .useSectionPath('main > div > article > div > div > div:first-child > article > div:last-child') \
                .useTitlePath('div a.linkbox__overlay') \
                .useDatePath('div footer > div:first-child time:first-child', in_date_format = '%b %d, %Y') \
                .useLinkPath('div a.linkbox__overlay') \
                .scrape_in(week=targetNumWeek)

        blogs_list.extend(first_blogs_list)
        if not within_week_search:
            return

        # Second article session
        second_blogs_list, within_week_search = \
            WebSection(driver) \
                .useSectionPath('main > div > article > div > div > div:not(:first-child) div.grow') \
                .useTitlePath('div a.linkbox__overlay') \
                .useDatePath('div footer > div:first-child time:first-child', in_date_format = '%b %d, %Y') \
                .useLinkPath('div a.linkbox__overlay') \
                .scrape_in(week=targetNumWeek)

        blogs_list.extend(second_blogs_list)
        if not within_week_search:
            return

        # Third article section
        third_web_section = WebSection(driver) \
                                .useSectionPath('main > div > div:last-child > div > article > article') \
                                .useTitlePath('div:last-child article h3 span') \
                                .useDatePath('div:first-child > h4', in_date_format = '%b %d, %Y') \
                                .useLinkPath('div:last-child article h3 a')

        while(True):
            # Get last post's date
            last_article_date = third_web_section.scrape_last()[0]

            # Check for the last post's published date, if within the target week, keep loading more contents
            if (datetime.now() - last_article_date) > timedelta(weeks=targetNumWeek):
                # print(f'DEBUG: Last article of {url} is within the target week')
                third_blogs_list, _ = third_web_section.scrape_in(week=targetNumWeek)
                blogs_list.extend(third_blogs_list)

                break
            else:
                # Load more stories
                # print('DEBUG: Loading more stories...')
                load_more_btn = driver.find_element(By.CSS_SELECTOR, 'main > div > div:last-child > div > article button')
                load_more_btn.send_keys(Keys.ENTER)
                time.sleep(delay)


    for url in pageUrl:
        scrapeSection(url)
        # blogs_list.append(['\n'])
        writeFileData(blogs_list, targetNumWeek)
        blogs_list.clear()

    # Write data into file
    print('Scraping Decrypt Finished')
    driver.quit()


def scrapeNewsExplorer(targetNumWeek):
    print('Starting scraping News Explorer...')
    pageUrl = ['https://decrypt.co/news-explorer']
    driver = webdriver.Chrome(options=create_option())
    blogs_list = []
    
    delay = 2

    writeFileTitle('News Explorer')
    
    def format_post_date(date):
            # Article format: Feb 7, 6:58 pm
            date = date.split(',')[0]
            date = datetime.strptime(date, '%b %d')
            date = date.replace(year = datetime.now().year)
            return date

    def scrapeSection(url):
        print(f'working on: {url}')
        driver.get(url)
        time.sleep(delay)

        # Articles
        articles_section = WebSection(driver) \
                            .useSectionPath('.-mx-4 > div') \
                            .useTitlePath('h4') \
                            .useDatePath('div:nth-child(1) > div:nth-child(1) > div:nth-child(1)',
                                        custom_date_format = format_post_date) \
                            .useLinkPath('div:nth-child(2) > div:nth-child(1) > a:nth-child(1)')

        while(True):
            # Get last post's date
            last_article_date = articles_section.scrape_last()[0]

            # Check for the last post's published date, if within the target week, keep loading more contents
            if (datetime.now() - last_article_date) > timedelta(weeks=targetNumWeek):
                # print(f'DEBUG: Last article of {url} is within the target week')
                articles_list, _ = articles_section.scrape_in(week=targetNumWeek)
                blogs_list.extend(articles_list)

                break
            else:
                # Load more stories
                # print('DEBUG: Loading more stories...')
                load_more_btn = driver.find_element(By.CSS_SELECTOR, '.my-2')
                load_more_btn.send_keys(Keys.ENTER)
                time.sleep(delay)


    for url in pageUrl:
        scrapeSection(url)
        writeFileData(blogs_list, targetNumWeek)
        blogs_list.clear()
    
    # Quit driver
    print('Scraping Decrypt Finished')
    driver.quit()
