from selenium import webdriver
from selenium.webdriver.common.by import By
from datetime import datetime
from Utils.driver_options import create_option
from Utils.write_to_list import writeScrapedData
from Utils.correct_time_offset import correctTimeOffset
from globals import fileName, outputDateFormat
import time


def scrapeAliAbdaal(targetNumWeek):
    print('@Ali Abdaal')
    url = "https://aliabdaal.com/articles/page/"
    curPg = 1
    delay = 2
    dateFormat = '%B %d, %Y'
    isEnough = False

    postPath = 'div[style="box-shadow: rgba(149, 157, 165, 0.2) 0px 8px 24px;"]'
    postUrlPath = 'a'
    postTitlePath = 'h3'
    postDatePath = 'h4'
    
    # driver = webdriver.Chrome()
    driver = webdriver.Chrome(options=create_option())

    dataList = []
    while curPg <= 11:
        driver.get(url + str(curPg) + '/')
        time.sleep(delay)

        # posts = driver.find_elements(By.CSS_SELECTOR, postPath)
        for post in driver.find_elements(By.CSS_SELECTOR, postPath):
            postUrl = post.find_element(By.CSS_SELECTOR, postUrlPath).get_attribute('href')
            postTitle = post.find_element(By.TAG_NAME, postTitlePath).text
            postDate = post.find_element(By.TAG_NAME, postDatePath).text

            # postDate = postDate.split(' ')
            # if len(postDate[1]) == 2:
            #         postDate[1] = '0' + postDate[1]
            # postDate = ' '.join(postDate)

            if not correctTimeOffset(postDate, dateFormat, targetNumWeek):
                print('* enough post')
                isEnough = True
                break
            
            postDate = datetime.strftime(datetime.strptime(postDate, dateFormat), outputDateFormat)
            dataRow = [postDate, postTitle, postUrl]
            # print(dataRow)

            dataList.append(dataRow)
        
        # break
        if isEnough:
            break

        curPg += 1
        print('* still searching')

    writeScrapedData('Ali Abdaal', fileName, dataList, targetNumWeek)
    print('> done')
    driver.quit()
