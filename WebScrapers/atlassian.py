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

def scrapeAtlassian(targetNumWeek):
    print('@Atlassian')
    write_to_list.writeFileTitle("=== Atlassian ===")
    
    pageUrlBase = 'https://www.atlassian.com/blog/'
    pageTopics = [
        'teamwork/',
        'leadership/',
        'strategy/',
        'productivity/',
    ]

    dateFormat = '%Y-%m-%d'
    postDivPathList = [
        'div[class="grid-column col-md-6 col-lg-4"]',
        'div[class="grid-column col-sm-6"]', 
        'div[class="grid-column col-lg-4"]',
    ]
    postUrlPath = 'a'
    postTitlePath = 'h1[class="post-title"]'
    postDatePath = 'time[class="entry-date published updated"]'
    
    driver = webdriver.Chrome(options=create_option())
    
    for topic in pageTopics:
        pageUrlTopic = pageUrlBase + topic
        print(f'>>> {pageUrlTopic}')
        write_to_list.writeFileTitle(f'> {pageUrlTopic}')
        
        dataList = []
        curPage = 1
        while True:
            isEnough = False
            pageUrl = pageUrlTopic + 'page/' + str(curPage)
            
            driver.get(pageUrl)
            time.sleep(2)
            
            # retrieve post divs
            postDivList = []
            for postDivPath in postDivPathList:
                postDivList += driver.find_elements(By.CSS_SELECTOR, postDivPath)
            
            for postDiv in postDivList:
                postUrl = postDiv.find_element(By.CSS_SELECTOR, postUrlPath).get_attribute('href')
                # print(f'* {postUrl}')
                
                # new tab
                driver.execute_script(f'window.open("{postUrl}","_blank");')
                time.sleep(2)
                driver.switch_to.window(driver.window_handles[1])
                
                #get title + date
                postTitle = driver.find_element(By.CSS_SELECTOR, postTitlePath).text
                postDate = driver.find_element(By.CSS_SELECTOR, postDatePath).get_attribute('datetime')
                postDate = postDate[:10]
                
                if not correctTimeOffset(postDate, dateFormat, targetNumWeek):
                    print("* enough posts")
                    isEnough = True
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                    break
                
                # postDate = datetime.strftime(datetime.strptime(postDate, dateFormat), outputDateFormat)
                dataRow = [postDate, postTitle, postUrl]
                # print(dataRow)
                
                dataList.append(dataRow)
                
                # close tab 
                driver.close()
                driver.switch_to.window(driver.window_handles[0])

            if isEnough:
                break
            curPage += 1
    
        write_to_list.writeFileData(dataList, targetNumWeek)
        
    print('> done')
    driver.quit()
    return