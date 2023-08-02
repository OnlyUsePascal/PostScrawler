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

def scrapeKdnugget(targetNumWeek):
    print('@Kdnugget')
    write_to_list.writeFileTitle("=== Kdnugget ===")
    
    pageUrl = 'https://www.kdnuggets.com/'
    
    dateFormat = '%B %d, %Y'
    boardInfos = [
        ['Latest', 'table[class="thb"][width="100%"][cellpadding="3"]'],
        ['Top in last 30 days', 'table[cellpadding="3"][cellspacing="2"]'],
        ['More latest', 'div[class="latn"][style="margin-top: 30px;"]'],
    ]
    postPath = 'li'
    postUrlPath = 'a'
    postTitlePath = 'h1'
    postDatePath = 'div[class="author-link"]'
    
    # driver = webdriver.Chrome()
    driver = webdriver.Chrome(options=create_option())
    driver.get(pageUrl)
    
    for boardInfo in boardInfos:
        boardTitle = boardInfo[0]
        boardPath = boardInfo[1] 
        
        print(f'> {boardTitle}')
        write_to_list.writeFileTitle(f"> {boardTitle}")
        
        board = driver.find_element(By.CSS_SELECTOR, boardPath)
        dataList = []
        for post in board.find_elements(By.CSS_SELECTOR, postPath):
            postUrl = post.find_element(By.CSS_SELECTOR, postUrlPath).get_attribute('href')
            
            if (pageUrl not in postUrl):
                continue
            
            # new tab
            driver.execute_script(f'window.open("{postUrl}","_blank");')
            driver.switch_to.window(driver.window_handles[1])
            time.sleep(2)
            
            # get data
            postTitle = driver.find_element(By.CSS_SELECTOR, postTitlePath).text
            postDate = driver.find_element(By.CSS_SELECTOR, postDatePath).text
            
            n1 = postDate.find(' on ')
            n2 = postDate.find(' in ')
            postDate = postDate[n1 + len(' on '):n2]
            if len(postDate[1]) == 2:
                postDate[1] = '0' + postDate[1]
                postDate = ' '.join(postDate)

            if not correctTimeOffset(postDate, dateFormat, targetNumWeek):
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                continue
            
            postDate = datetime.strftime(datetime.strptime(postDate, dateFormat), outputDateFormat)
            dataRow = [postDate, postTitle, postUrl]
            dataList.append(dataRow)
            # print(dataRow)
            
            # close tab
            driver.close()
            driver.switch_to.window(driver.window_handles[0])

        write_to_list.writeFileData(dataList, targetNumWeek)
    return
    print('@Webflow')
    
    pageUrlBase = 'https://webflow.com/category/'
    pageUrlEnds = [
        'entrepreneurship',
        'tools-resources',
    ]

    dateFormat = '%B %d, %Y'
    postPath = 'a[class="blog-card_post-link w-inline-block"]'
    postTitlePath = 'h1[class="b-post__head"]'
    postDatePath = 'h2[class="h4 u-mb-0"]'
    btnNextPgPath = 'a[aria-label="Next Page"]'
    
    # driver = webdriver.Chrome()
    driver = webdriver.Chrome(options=create_option())

    # for each endpoint
    for pageUrlEnd in pageUrlEnds:
        pageUrl = pageUrlBase + pageUrlEnd
        write_to_list.writeFileTitle(f'> {pageUrl}')
        print(f'> {pageUrl}')

        driver.get(pageUrl)
        time.sleep(2)
        
        isEnough = False
        dataList = []
        while True:
            # for each post
            postUrls = driver.find_elements(By.CSS_SELECTOR, postPath)      
            for postUrl in postUrls:
                postUrl = postUrl.get_attribute('href')
                # print(f'< {postUrl}')
                
                # new tab 
                driver.execute_script(f'window.open("{postUrl}","_blank");')
                time.sleep(2)
                driver.switch_to.window(driver.window_handles[1])
                
                # get title + date
                postTitle = driver.find_element(By.CSS_SELECTOR, postTitlePath).text
                postDate = driver.find_element(By.CSS_SELECTOR, postDatePath).text.split(' ')
                if len(postDate[1]) == 2:
                    postDate[1] = '0' + postDate[1]
                postDate = ' '.join(postDate)
                
                # process date
                if not correctTimeOffset(postDate, dateFormat, targetNumWeek):
                    print("* enough posts")
                    isEnough = True
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                    break
                
                postDate = datetime.strftime(datetime.strptime(postDate, dateFormat), outputDateFormat)
                dataRow = [postDate, postTitle, postUrl]
                # print(dataRow)
                dataList.append(dataRow)
                
                # close tab
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
            
            # if not enough, move next page
            if isEnough:
                break
            
            try:
                print('* next page')
                btnNextPg = driver.find_element(By.CSS_SELECTOR, btnNextPgPath)
                driver.execute_script("arguments[0].click();", btnNextPg)
                time.sleep(2)
            except Exception as err:
                print('* end page reached')
                break
        
        write_to_list.writeFileData(dataList, targetNumWeek)
        
    print('> done')
    driver.quit()
