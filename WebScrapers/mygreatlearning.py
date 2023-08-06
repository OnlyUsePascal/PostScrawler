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

def scrapeMygreatlearning(targetNumWeek):
    print('@My Great Learning')
    write_to_list.writeFileTitle("=== My Great Learning ===")
    
    pageUrlBase = 'https://www.mygreatlearning.com/blog/'
    pageUrlEndpoints = [
        'artificial-intelligence/', 
        'career/',
        'data-science/', 
        'cybersecurity/',
        'software/', 
        'digital-marketing/',
        'businessmanagement/',
        'cloud-computing/',
        'interview-questions/',
        'study-abroad/',
    ]    
    
    dateFormat = '%b %d, %Y'
    postPath = 'article[class="post"]'
    postTitlePath = 'h3'
    postDatePath = 'span[class="date"]'
    postUrlPath = 'a'
    maxPostNum = 6
    maxScroll = 3

    # driver = webdriver.Chrome()
    driver = webdriver.Chrome(options=create_option())

    for endpoint in pageUrlEndpoints:
        print(f'> {pageUrlBase + endpoint}')
        write_to_list.writeFileTitle(f'> {pageUrlBase + endpoint}')
        
        curPg = 1
        dataList = []
        curScroll = 0
        isEnough = False
        
        while True:
            pageUrl = pageUrlBase + endpoint + f'page/{curPg}'
            oldLen = len(dataList)
            
            driver.get(pageUrl)
            time.sleep(2) 
            
            for post in driver.find_element(By.CSS_SELECTOR, 'div[class="posts"]').find_elements(By.CSS_SELECTOR, postPath):
                postTitle = post.find_element(By.CSS_SELECTOR, postTitlePath).text
                postUrl = post.find_element(By.CSS_SELECTOR, postUrlPath).get_attribute('href')
                postDate = post.find_element(By.CSS_SELECTOR, postDatePath).text[11:].split(' ')
                if len(postDate[1]) == 2:
                    postDate[1] = '0' + postDate[1]
                postDate = ' '.join(postDate)
                
                # validate
                if not correctTimeOffset(postDate, dateFormat, targetNumWeek):
                    continue
                    
                postDate = datetime.strftime(datetime.strptime(postDate, dateFormat), outputDateFormat)
                dataRow = [postDate, postTitle, postUrl]
                dataList.append(dataRow)
                # print(dataRow)
                
                if len(dataList) >= maxPostNum:
                    # print("* enough posts")
                    isEnough = True
                    break
                    
            
            # in case not patient scroll page
            if (len(dataList) == oldLen):
                curScroll += 1
                if (curScroll >= maxScroll):
                    # print('* enough scroll') 
                    break
            else:
                curScroll = 1
            
            # enough post
            if isEnough:
                break            
            
            # print('* next page')
            curPg += 1
        
        write_to_list.writeFileData(dataList, targetNumWeek)
    
    print('> done')
    driver.quit()
    