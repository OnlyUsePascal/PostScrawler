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

def scrapeCognizant(targetNumWeek):
    print('@Cognizant')
    write_to_list.writeFileTitle("=== Cognizant ===")
    
    pageUrl = 'https://digitally.cognizant.com/home'

    dateFormat = '%b %d, %Y'
    postPath = 'div[class="card-section p0 h100"]'
    postDatePath = 'p[class="small text-gray pt-qtr"]'
    postUrlPath = 'a[class="text-blue"]'
    postTitlePath = 'h6'
    btnNextPgPath = 'a[id="nextButton"]'
    
    # driver = webdriver.Chrome()
    driver = webdriver.Chrome(options=create_option())
    driver.get(pageUrl)
    time.sleep(3)
    
    isEnough = False
    dataList = []
    while True:
        for post in driver.find_elements(By.CSS_SELECTOR, postPath):
            postTitle = post.find_element(By.CSS_SELECTOR, postTitlePath).text
            postUrl = post.find_element(By.CSS_SELECTOR, postUrlPath).get_attribute('href')
            postDate = post.find_element(By.CSS_SELECTOR, postDatePath).text[:12]
            
            if not correctTimeOffset(postDate, dateFormat, targetNumWeek):
                print("* enough posts")
                isEnough = True
                break
            
            postDate = datetime.strftime(datetime.strptime(postDate, dateFormat), outputDateFormat)
            dataRow = [postDate, postTitle, postUrl]
            dataList.append(dataRow)
            # print(dataRow)
            
        if isEnough:
            break
        
        print('> next page')
        btnNextPg = driver.find_element(By.CSS_SELECTOR, btnNextPgPath)
        driver.execute_script("arguments[0].click();", btnNextPg)
        time.sleep(2)
    
    write_to_list.writeFileData(dataList, targetNumWeek)
    
    print('> done')
    driver.quit()
