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
    # FUTURE ME: URL STRUCTURE TO PAGE INSTEAD OF LOADING
    print('@My Great Learning')
    write_to_list.writeFileTitle("=== My Great Learning ===")
    
    pageUrlBase = 'https://www.mygreatlearning.com/blog/'
    pageUrlEndpoints = [
        # 'career/',
        # 'data-science/', 
        # 'cybersecurity/',
        
        'artificial-intelligence/', 
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
    btnMorePath = 'a[class="load-more"]'
    maxPostNum = 6
    maxScroll = 3

    driver = webdriver.Chrome()
    # driver = webdriver.Chrome(options=create_option())

    for endpoint in pageUrlEndpoints:
        pageUrl = pageUrlBase + endpoint
        print(f'> {pageUrl}')
        write_to_list.writeFileTitle(f'> {pageUrl}')
        
        driver.get(pageUrl)
        time.sleep(2)
        
        dataList = []
        curScroll = 0
        while True:
            posts = driver.find_element(By.CSS_SELECTOR, 'div[class="posts"]').find_elements(By.CSS_SELECTOR, postPath)
            dataList = []
            curScroll += 1
            
            for post in posts:
                postTitle = post.find_element(By.CSS_SELECTOR, postTitlePath).text
                postUrl = post.find_element(By.CSS_SELECTOR, postUrlPath).get_attribute('href')
                postDate = post.find_element(By.CSS_SELECTOR, postDatePath).text[11:].split(' ')
                if len(postDate[1]) == 2:
                    postDate[1] = '0' + postDate[1]
                postDate = ' '.join(postDate)

                # validate
                if not correctTimeOffset(postDate, dateFormat, targetNumWeek):
                    continue
                
                # true
                curScroll = 0
                postDate = datetime.strftime(datetime.strptime(postDate, dateFormat), outputDateFormat)
                dataRow = [postDate, postTitle, postUrl]
                dataList.append(dataRow)
                # print(dataRow)

            if len(dataList) >= maxPostNum:
                print("* enough posts")
                break
            
            if curScroll >= maxScroll:
                print('* enough scroll')
                break
        
            # more post btn
            # print('* more post')
            try:
                btnMore = driver.find_element(By.CSS_SELECTOR, btnMorePath)
                driver.execute_script("arguments[0].click();", btnMore)
            
                curSz = len(posts)
                while True:
                    newSz = len(driver.find_element(By.CSS_SELECTOR, 'div[class="posts"]').find_elements(By.CSS_SELECTOR, postPath))            
                    if (newSz != curSz):
                        break
                    time.sleep(2)
            except Exception:
                break
    
        write_to_list.writeFileData(dataList, targetNumWeek)
    
    print('> done')
    driver.quit()