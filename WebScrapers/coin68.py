import time
from datetime import datetime, timedelta
from selenium import webdriver
from Utils.SectionScrape.scrape_section import WebSection
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import csv
from Utils.driver_options import create_option
from Utils.error_handler import handle_scrape_errors
from Utils.write_to_list import writeFileTitle, writeFileData
from selenium.webdriver.support import expected_conditions as EC
from Utils.write_to_list import writeScrapedData
from globals import fileName, outputDateFormat
from selenium.webdriver.support.ui import WebDriverWait
from Utils.correct_time_offset import correctTimeOffset


@handle_scrape_errors
def startScrape(targetNumWeek):
    siteTitle = 'Coin68'
    print(f'=== {siteTitle} ===')
    writeFileTitle(siteTitle)
    
    url = 'https://coin68.com/article/'
    endpoints = [
        'big-cap/', 
        'defi/', 
        'nft-gamefi/', 
        'phap-ly/', 
        'tin-tong-hop/',
    ]
    delay = 2
    dateFormat = '%d/%m/%Y'
    isEnough = True

    postPath = 'div[class="MuiBox-root css-1kdy0wu"]'
    postTitlePath = 'a'
    # postUrlPath = 'a'
    postDatePath = 'p'
    pgBtnPath = 'button[aria-label="Go to next page"]'
    
    service = Service(ChromeDriverManager().install())
    options = create_option(headless=True)
    driver = webdriver.Chrome(options=options, service=service)
    
    curPg = 1
    isEnough = False
    # isAdClosed = False
    
    for endpoint in endpoints:
        dataList = []
        urlFull = url + endpoint
        print(f'> {urlFull}')
        with open(fileName, 'a', encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow([f'> {urlFull}'])
        
        driver.get(urlFull)
        time.sleep(delay)
        
        while True:
            posts = driver.find_elements(By.CSS_SELECTOR, postPath)
            for post in posts:
                postTitle = post.find_element(By.CSS_SELECTOR, postTitlePath).text
                postUrl = post.find_element(By.CSS_SELECTOR, postTitlePath).get_attribute('href')
                postDate = post.find_element(By.CSS_SELECTOR, postDatePath).text
                
                if (postTitle[-3:] == '...'):
                    driver.execute_script(f'window.open("{postUrl}","_blank");')
                    driver.switch_to.window(driver.window_handles[1])
                    postTitle = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'h1[class="MuiTypography-root MuiTypography-h1 css-pdjcgu"]'))).text
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                    time.sleep(1)
                    
                # if (postDate == ''):
                #   print('> err: blank page, pls try again')
                #   return
                #   continue
                # postDate = postDate.split(' ')
                # if len(postDate[1]) == 2:
                #   postDate[1] = '0' + postDate[1]
                # postDate = ' '.join(postDate)
                
                # print([postDate, postTitle, postUrl])
                if not correctTimeOffset(postDate, dateFormat, targetNumWeek):
                    print('+ enough post')
                    isEnough = True
                    break 
                
                dataRow = [postDate, postTitle, postUrl]
                postDate = datetime.strftime(datetime.strptime(postDate, dateFormat), outputDateFormat)
                dataList.append(dataRow)
                # print(dataRow)
                
            if isEnough:
                print('> done\n')
                # writeScrapedData(siteTitle, fileName, dataList, targetNumWeek)
                writeFileData(dataList, targetNumWeek)
                # driver.quit()
                break
            
            print('+ still searching')
            # curPg += 1
            # pgBtnPath = f'a[href="/bytes/archive?page={curPg}"]'
            # driver.execute_script("arguments[0].click();", driver.find_element(By.XPATH, pgBtnPath))
            WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.CSS_SELECTOR, pgBtnPath))).click()
            # driver.find_element(By.XPATH, pgBtnPath).send_keys(Keys.ENTER)
            time.sleep(2)
        