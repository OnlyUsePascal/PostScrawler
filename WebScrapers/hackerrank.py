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

def scrapeHackerrank(targetNumWeek):
    print('@HackerRank')
    write_to_list.writeFileTitle("=== HackerRank ===")
    
    pageUrlBase = 'https://www.hackerrank.com/blog/page/'
    curPage = 1
    # pageUrlEnds = [
    #     'entrepreneurship',
    #     'tools-resources',
    # ]

    dateFormat = '%B %d, %Y'
    boardPath = 'div[class="blog_listing-list"]'
    postDivPath = 'div[class="hr_post"]'
    postUrlPath = 'a[class="hr_post-content"]'
    postTitlePath = 'h1[class="hr_post_page-title"]'
    postDatePath = 'div[class="hr_post_page-author"]'
    
    # driver = webdriver.Chrome()
    driver = webdriver.Chrome(options=create_option())
    dataList = []

    # for each page
    while True:
        pageUrl = pageUrlBase + str(curPage)
        print(f'> {pageUrl}')

        driver.get(pageUrl)
        time.sleep(2)
        
        isEnough = False
        board = driver.find_element(By.CSS_SELECTOR, boardPath)
        
        # for each post
        while True:
            for postDiv in board.find_elements(By.CSS_SELECTOR, postDivPath):
                postUrl = postDiv.find_element(By.CSS_SELECTOR, postUrlPath).get_attribute('href')
                
                # new tab
                driver.execute_script(f'window.open("{postUrl}","_blank");')
                time.sleep(2)
                driver.switch_to.window(driver.window_handles[1])
                
                #get title + date
                postTitle = driver.find_element(By.CSS_SELECTOR, postTitlePath).text
                postDate = driver.find_element(By.CSS_SELECTOR, postDatePath).text.split(' | ')[-1].split(' ')
                if len(postDate[1]) == 2:
                    postDate[1] = '0' + postDate[1]
                postDate = ' '.join(postDate)
                
                
                if not correctTimeOffset(postDate, dateFormat, targetNumWeek):
                    print("* enough posts")
                    isEnough = True
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                    break
                
                postDate = datetime.strftime(datetime.strptime(postDate, dateFormat), outputDateFormat)
                dataRow = [postDate, postTitle, postUrl]
                print(dataRow)
                
                dataList.append(dataRow)
                
                # close tab 
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
            break
    
        # if not enough, move next page
        if isEnough:
            break
            
        curPage += 1
    
    write_to_list.writeFileData(dataList, targetNumWeek)
        
    print('> done')
    driver.quit()