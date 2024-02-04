from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from datetime import datetime
from Utils.driver_options import create_option
from Utils.write_to_list import writeScrapedData
from Utils.correct_time_offset import correctTimeOffset
from globals import fileName, outputDateFormat
import time

def startScrape(targetNumWeek):
    siteTitle = 'The Block 1'
    print(siteTitle)
    
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
        print(urlAll)
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

    writeScrapedData(siteTitle, fileName, dataList, targetNumWeek)
    print('> done')
    driver.quit()
