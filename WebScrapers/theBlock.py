from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.common.by import By
from datetime import datetime
from Utils.driver_options import create_option
from Utils.write_to_list import writeScrapedData
from Utils.correct_time_offset import correctTimeOffset
from globals import fileName, outputDateFormat
import time

# Phuc
def scrapeLatest(targetNumWeek):
    siteTitle = 'The Block Latest'
    print('--> ' + siteTitle)
    
    url = "https://www.theblock.co/learn/latest/"
    curPg = 1
    delay = 2
    dateFormat = '%B %d %Y'
    isEnough = False

    postPath = '.articleList__categoryCardContainer > div'
    postUrlPath = 'a:nth-child(1)'
    postTitlePath = 'a.card__link div.card div.card__container div.card__titleWrapperBase div.card__title'
    postDatePath = 'a:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > div:nth-child(2)'
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(options=create_option(headless=True), service=service)

    dataList = []
    while True:

        urlAll = url + str(curPg)
        print(f'> {urlAll}')
        driver.get(urlAll)
        time.sleep(delay)

        isBlank = True
        for post in driver.find_elements(By.CSS_SELECTOR, postPath):
            # print('DEBUGTIME')
            isBlank = False
            postUrl = post.find_element(By.CSS_SELECTOR, postUrlPath).get_attribute('href')
            postTitle = post.find_element(By.CSS_SELECTOR, postTitlePath).text
            postDate = post.find_element(By.CSS_SELECTOR, postDatePath).text

            postDate = postDate.split(', ')[:-1]
            postDate = ' '.join(postDate)
            postDate = postDate.split(' ')
            if len(postDate[1]) == 1:
                    postDate[1] = '0' + postDate[1]
            postDate = ' '.join(postDate)

            if not correctTimeOffset(postDate, dateFormat, targetNumWeek):
                print('* enough post')
                isEnough = True
                break

            postDate = datetime.strftime(datetime.strptime(postDate, dateFormat), outputDateFormat)
            dataRow = [postDate, postTitle, postUrl]
            # print(dataRow)
            dataList.append(dataRow)

        if isEnough or isBlank:
            break

        curPg += 1
        print('* still searching')

    writeScrapedData(siteTitle, fileName, dataList, targetNumWeek, url)
    print('> done\n')
    driver.quit()

# Dat
def startScrapeReport(targetNumWeek):
    siteTitle = 'The Block Reports'
    print('--> ' + siteTitle)
    
    url = "https://www.theblock.co/reports?start="
    curPg = 0
    delay = 2
    dateFormat = '%B %d %Y'
    isEnough = False

    postPath = 'div[class="cardContainer"]'
    postUrlPath = 'a'
    postTitlePath = 'h2'
    postDatePath = 'div[class="pubDate"]'
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(options=create_option(headless=True), service=service)

    dataList = []
    while True:
        
        urlAll = url + str(curPg * 10)
        print(f'> {urlAll}')
        driver.get(urlAll)
        time.sleep(delay)
        
        isBlank = True
        for post in driver.find_elements(By.CSS_SELECTOR, postPath):
            isBlank = False
            postUrl = post.find_element(By.TAG_NAME, postUrlPath).get_attribute('href')
            postTitle = post.find_element(By.TAG_NAME, postTitlePath).text
            postDate = post.find_element(By.CSS_SELECTOR, postDatePath).text

            postDate = postDate.split(', ')[:-1]
            postDate = ' '.join(postDate)
            postDate = postDate.split(' ')
            if len(postDate[1]) == 1:
                    postDate[1] = '0' + postDate[1]
            postDate = ' '.join(postDate)

            if not correctTimeOffset(postDate, dateFormat, targetNumWeek):
                print('* enough post')
                isEnough = True
                break
            
            postDate = datetime.strftime(datetime.strptime(postDate, dateFormat), outputDateFormat)
            dataRow = [postDate, postTitle, postUrl]
            # print(dataRow)
            dataList.append(dataRow)
        
        if isEnough or isBlank:
            break

        curPg += 1
        print('* still searching')

    writeScrapedData(siteTitle, fileName, dataList, targetNumWeek, url)
    print('> done\n')
    driver.quit()
