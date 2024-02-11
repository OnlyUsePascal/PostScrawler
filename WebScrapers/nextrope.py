import time
from datetime import datetime, timedelta
from selenium import webdriver
from Utils.SectionScrape.scrape_section import WebSection
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from Utils.driver_options import create_option
from Utils.write_to_list import writeFileTitle, writeFileData


def scrapeArticles(targetNumWeek):
    print('---> Nextrope')
    pageUrl = ['https://nextrope.com/blog/']
    
    service = Service(ChromeDriverManager().install())
    options = create_option(headless=True)
    driver = webdriver.Chrome(options=options, service=service)
    blogs_list = []
    
    delay = 2

    writeFileTitle('Nextrope')


    def scrapeSection(url):
        print(f'> {url}')
        writeFileTitle(f'> {url}', no_decoration=True)
        driver.get(url)
        time.sleep(delay)

        # Articles
        articles_section = WebSection(driver) \
                            .useSectionPath('#blog-container > div') \
                            .useTitlePath('h1.content_header__title:nth-child(2)') \
                            .useDatePath('div.gap-4:nth-child(3) > div:nth-child(2) > span:nth-child(2)', in_date_format='%d %b %Y') \
                            .useLinkPath('div:nth-child(1) > a:nth-child(1)') \
                            .as_link(True)

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
                print('+ more stories...')
                load_more_btn = driver.find_element(By.CSS_SELECTOR, '#load-more-posts')
                load_more_btn.send_keys(Keys.ENTER)
                time.sleep(delay)


    for url in pageUrl:
        scrapeSection(url)
        writeFileData(blogs_list, targetNumWeek)
        blogs_list.clear()
    
    # Quit driver
    print('> Done\n')
    driver.quit()
