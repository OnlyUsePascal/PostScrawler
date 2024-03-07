from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from datetime import datetime, time, timedelta
from Utils.error_handler import handle_scrape_errors, open_with_retries
from Utils.driver_options import create_option
from Utils.correct_time_offset import correctTimeOffset
from globals import fileName, outputDateFormat
from gc import isenabled
from pickle import FALSE
from selenium import webdriver
from Utils.write_to_list import writeFileData, writeFileTitle, writeMessage, writeScrapedData
from globals import fileName, outputDateFormat
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

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
    
    
@handle_scrape_errors
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


@handle_scrape_errors
def startScrape(targetNumWeek : int):
    siteTitle = 'HakResearch'
    print('--> ' + siteTitle)
    writeFileTitle(siteTitle)
    
    url = 'https://hakresearch.com/nguoi-moi-2/'
    endpoints = [
        'khai-niem-co-ban/',
        'kinh-nghiem/',
        'huong-dan-co-ban/',
    ]
    delay = 3
    dateFormat = '%Y-%m-%d'
    
    postPath = 'article[class="l-post grid-post grid-base-post"]'
    postTitlePath = 'h2'
    postDatePath = 'time[class="post-date"]'
    
    service = Service(ChromeDriverManager().install())
    options = create_option(headless=False)
    driver = webdriver.Chrome(options=options, service=service)
    
    for endpoint in endpoints:
        print(f'> {url + endpoint}')
        writeMessage(fileName, f'> {url + endpoint}')
        curPg = 1
        isEnough = False
        dataList = []
        
        while True:
            urlAll = url + endpoint + '/page/' + str(curPg)
            driver.get(urlAll)
            time.sleep(delay)
            
            for post in driver.find_elements(By.CSS_SELECTOR, postPath):
                postTitle = post.find_element(By.TAG_NAME, postTitlePath).text
                postUrl = post.find_element(By.TAG_NAME, 'a').get_attribute('href')
                postDate = post.find_element(By.CSS_SELECTOR, postDatePath).get_attribute('datetime').split('T')[0]
                
                if not correctTimeOffset(postDate, dateFormat, targetNumWeek):
                    isEnough = True
                    break
            
                postDate = datetime.strftime(datetime.strptime(postDate, dateFormat), outputDateFormat)
                dataRow = [postDate, postTitle, postUrl]
                dataList.append(dataRow)
                print(dataRow)
                
            if isEnough:
                print('> done\n')
                writeFileData(dataList, targetNumWeek)
                # writeScrapedData(siteTitle + ':' + endpoint, fileName, dataList, targetNumWeek)
                break
            
            curPg += 1
            print('+ still searching')
        
    driver.quit()