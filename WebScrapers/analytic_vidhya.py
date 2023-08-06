import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from datetime import datetime
from Utils.driver_options import create_option
from Utils.write_to_list import writeScrapedData
from Utils.correct_time_offset import correctTimeOffset
from globals import fileName, outputDateFormat
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from Utils import write_to_list

def scrapeAnalytic_Vidhya(targetNumWeek):
    print('@Analytic Vidhya')
    write_to_list.writeFileTitle("=== Analytic Vidhya ===")
    
    pageUrlBase = 'https://www.analyticsvidhya.com/blog-archive/page/'
    curPg = 1
    
    dateFormat = '%B %d %Y'
    postPath = 'div[class="list-card-content"]'
    postTitlePath = 'h4'
    postUrlPath = 'a'
    postDatePath = 'h6'

    # driver = webdriver.Chrome()    
    driver = webdriver.Chrome(options=create_option())
    
    dataList = []
    isEnough = False
    while True:
        pageUrl = pageUrlBase + str(curPg)
        driver.get(pageUrl)
        time.sleep(2)
        
        for post in driver.find_elements(By.CSS_SELECTOR, postPath):
            postTitle = post.find_element(By.CSS_SELECTOR, postTitlePath).text
            postUrl = post.find_element(By.CSS_SELECTOR, postUrlPath).get_attribute('href')
            postDate = post.find_element(By.CSS_SELECTOR, postDatePath).text
            
            postDate = postDate.split(', ')
            postDate = (postDate[1] + ' ' + postDate[2]).split(' ')
            if len(postDate[1]) == 1:
                postDate[1] = '0' + postDate[1]
            postDate = ' '.join(postDate)
                        
            if not correctTimeOffset(postDate, dateFormat, targetNumWeek):
                # print("* enough posts")
                isEnough = True
                break
            
            postDate = datetime.strftime(datetime.strptime(postDate, dateFormat), outputDateFormat)
            dataRow = [postDate, postTitle, postUrl]
            # print(dataRow)
            
            dataList.append(dataRow)
        
        if isEnough:
            break
        
        # more page
        # print('* next page')
        curPg += 1
        
    write_to_list.writeFileData(dataList, targetNumWeek)
    print('> done')
    driver.quit()
    return