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

# @handle_scrape_errors()
def scrapeHubspot(targetNumWeek):
    print('@HubSpot')
    write_to_list.writeFileTitle('=== Hubspot ===')
    
    pageUrlPatterns = [
        ['https://blog.hubspot.com/the-hustle/page/','?hubs_content=blog.hubspot.com%2F&hubs_content-cta=null'],
        ['https://blog.hubspot.com/service/page/','?hubs_content=blog.hubspot.com%252F&hubs_content-cta=null&hubs_post-cta=blognavcard-service'],
        ['https://blog.hubspot.com/sales/page/','?hubs_content=blog.hubspot.com%252F&hubs_content-cta=null&hubs_post-cta=blognavcard-sales'],
        ['https://blog.hubspot.com/website/page/','?hubs_content=blog.hubspot.com%252F&hubs_content-cta=null&hubs_post-cta=blognavcard-website'],
        ['https://blog.hubspot.com/marketing/page/','?hubs_content=blog.hubspot.com%2525252525252F&hubs_content-cta=null&hubs_post-cta=blognavcard-marketing'],
    ]
    
    # driver = webdriver.Chrome()
    driver = webdriver.Chrome(options=create_option())
    
    dateFormat = '%B %d, %Y'
    postPath = 'li[class="blog-post-list-item"]'
    postUrlPath = 'a'
    postTitlePath = 'a'
    postDatePath = 'div[class="blog-post-header-dates"] time'
    
    for pageUrlPattern in pageUrlPatterns:
        print(f'> {pageUrlPattern[0]}')
        write_to_list.writeFileTitle(f'> {pageUrlPattern[0]}')
        
        curPage = 1
        dataList = []
        isEnough = False

        while True:
            pageUrl = pageUrlPattern[0] + str(curPage) + pageUrlPattern[1]

            driver.get(pageUrl)
            time.sleep(2)
            
            for post in driver.find_elements(By.CSS_SELECTOR, postPath):
                postUrl = post.find_element(By.CSS_SELECTOR, postUrlPath).get_attribute('href')
                postTitle = post.find_element(By.CSS_SELECTOR, postTitlePath).text
                
                # new tab 
                driver.execute_script(f'window.open("{postUrl}","_blank");')
                time.sleep(2)
                driver.switch_to.window(driver.window_handles[1])
                
                try:
                    postDate = driver.find_element(By.CSS_SELECTOR, postDatePath).text

                    # validate 
                    if not correctTimeOffset(postDate, dateFormat, targetNumWeek):
                        print("* enough posts")
                        isEnough = True
                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])
                        break
                    
                    postDate = datetime.strftime(datetime.strptime(postDate, dateFormat), outputDateFormat)
                    dataRow = [postDate,postTitle, postUrl]
                    # print(dataRow)
                    dataList.append(dataRow)
                except Exception as err:
                    print(f'* woops, some err happens')
                    # print(err)
                    
                # close tab
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
            
            if isEnough:
                break            
            
            print('* next page')
            curPage += 1 
    
        write_to_list.writeFileData(dataList,targetNumWeek)
        
    driver.quit()
    print('> Done')
    
    return 