from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from datetime import datetime, time, timedelta
from Utils.error_handler import handle_scrape_errors, open_with_retries
from Utils.driver_options import create_option
from Utils.write_to_list import writeScrapedData, writeFileTitle, writeFileData
from Utils.correct_time_offset import correctTimeOffset
import time
from globals import fileName, outputDateFormat


@handle_scrape_errors
def scrapeHakResearch1(targetNumWeek):
    print('Starting scraping Hakresearch: Kien thuc and He sinh thai...')
    kien_thuc_Urls = ['https://hakresearch.com/kien-thuc-2/danh-gia-du-an/',
                      'https://hakresearch.com/kien-thuc-2/phan-tich-chuyen-sau/',
                      'https://hakresearch.com/kien-thuc-2/co-che-hoat-dong/',
                      'https://hakresearch.com/kien-thuc-2/xu-huong-thi-truong/',
                      'https://hakresearch.com/kien-thuc-2/layer-2-kien-thuc-2/']
    he_sinh_thai_urls = [
        'https://hakresearch.com/he-sinh-thai/layer-1',
        'https://hakresearch.com/he-sinh-thai/layer-2',
        'https://hakresearch.com/he-sinh-thai/he-sinh-thai-giao-thuc/',
    ]

    driver = webdriver.Chrome(options=create_option())
    blogs_list = []
    
    def scrapeByEndpoints(url):
        print(f'working on: {url}')
        writeFileTitle(f"> {url}")

        blogs_list = []

        if not open_with_retries(driver, url):
            print(f'{url} not avaiable')
            writeFileData([], targetNumWeek)
            return

        # Wait until all blogs are presented on the web
        isEnough = False
        while True:
            try:
                blogs = WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.loop-grid-base.loop-grid article div.content')))
            except TimeoutException:
                print('Session take too long to load')
                break

            for blog in blogs:
                title = blog.find_element(By.CSS_SELECTOR, 'h2.post-title a').get_attribute('textContent')
                date = datetime.strptime(blog.find_element(By.CSS_SELECTOR, 'span.date span.date-link').get_attribute('textContent'), '%B %d, %Y')
                link = blog.find_element(By.CSS_SELECTOR, 'h2.post-title a').get_attribute('href')

                if (datetime.now() - date) > timedelta(weeks=targetNumWeek):
                    isEnough = True
                    break

                blogs_list.append([date.strftime(outputDateFormat), title, link])

            # enough post
            if isEnough:
                print("* enough post")
                break

            # Try if there is still more page to scrape
            try:
                next_page_btn = driver.find_element(By.CSS_SELECTOR, 'nav.pagination-numbers > a.next.page-numbers')
                next_page_btn.send_keys(Keys.ENTER)
            except Exception:
                return

        writeFileData(blogs_list, targetNumWeek)

    # scrape by sections
    print(">>> Kien thuc")
    writeFileTitle(">>> Kien thuc")
    for url in kien_thuc_Urls:
        scrapeByEndpoints(url)

    print(">>> He sinh thai")
    writeFileTitle(">>> He sinh thai")
    for url in he_sinh_thai_urls:
        scrapeByEndpoints(url)

    print('Scraping Hakresearch: Kien thuc Crypto Finished')
    driver.quit()
    

def scrapeHakResearch(targetNumWeek):
    writeFileTitle('=== Hak Research ===')
    print("@Hak Research")
    pageUrlBase = 'https://hakresearch.com/'
    
    postPath = 'article[class="l-post grid-post grid-base-post"]'
    postTitlePath = 'h2'
    postDatePath = 'span[class="date-link"]'
    postUrlPath = 'a'
    boardPageListPath = 'a[class="next page-numbers"]'
    dateFormat = '%B %d, %Y'

    driver = webdriver.Chrome(options=create_option())
    # driver = webdriver.Chrome()
    
    def scrapeBySection(pageUrlSection, pageUrlEnds):
        print(f'>>> {pageUrlSection}')
        writeFileTitle(f'>>> {pageUrlSection}')

        # for each ends
        for pageUrlEnd in pageUrlEnds:
            print(f'> {pageUrlEnd}')
            writeFileTitle(f'> {pageUrlEnd}')
            
            pageUrl = pageUrlBase + pageUrlSection + pageUrlEnd
            # pageUrl = 'https://hakresearch.com/kien-thuc-2/phan-tich-chuyen-sau/'
            isEnough = False
            dataList = []
            
            driver.get(pageUrl)
            time.sleep(2)
            
            while True:
                # scrape
                for post in driver.find_elements(By.CSS_SELECTOR, postPath):
                    postTitle = post.find_element(By.CSS_SELECTOR, postTitlePath).text
                    postUrl = post.find_element(By.CSS_SELECTOR, postUrlPath).get_attribute('href')
                        
                    # proceeed post date
                    postDate = post.find_element(By.CSS_SELECTOR, postDatePath).text.split(' ')
                    if len(postDate[1]) == 2:
                        postDate[1] = '0' + postDate[1]
                    postDate = ' '.join(postDate)
                    
                    # verify post date here
                    if not correctTimeOffset(postDate, dateFormat, targetNumWeek):
                        print('* enough post')
                        isEnough = True
                        break
                        
                    postDate = datetime.strftime(datetime.strptime(postDate, dateFormat), outputDateFormat)
                    data = [postDate, postTitle, postUrl]
                    # print(data)
                    dataList.append(data)
                    
                # if not enough, next page
                if isEnough:
                    break
                
                try:
                    nextPgBtn = driver.find_element(By.CSS_SELECTOR, boardPageListPath)
                    driver.execute_script("arguments[0].click();", nextPgBtn)
                    print('* next page')
                    time.sleep(2)
                except Exception:
                    print('* reached end page')
                    break
                
            # write data
            writeFileData(dataList, targetNumWeek)
    
    # call back with endpoints
    pageUrlSection = 'series-2/'
    pageUrlEnds = [
        'real-builder-in-winter',
        'phan-tich-on-chain',
        'macro-flow',
        'hidden-gem',
        'report',
        'quy-dau-tu',
        'nguoi-noi-tieng',
    ]
    scrapeBySection(pageUrlSection, pageUrlEnds)
    
    pageUrlSection = 'kiem-tien-2/'
    pageUrlEnds = [
        'retroactive2',
        'airdrop',
        'su-kien',
        'kien-thuc-kinh-nghiem/',
        'khac-kiem-tien/',
    ]
    scrapeBySection(pageUrlSection, pageUrlEnds)
    
    print('> Done')
    driver.quit()
