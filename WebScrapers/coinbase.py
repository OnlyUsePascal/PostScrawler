import time
from datetime import datetime, timedelta
from selenium import webdriver
from Utils.SectionScrape.scrape_section import WebSection
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from Utils.driver_options import create_option
from Utils.write_to_list import writeFileTitle, writeFileData
from selenium.webdriver.support import expected_conditions as EC
from Utils.write_to_list import writeScrapedData
from globals import fileName, outputDateFormat
from selenium.webdriver.support.ui import WebDriverWait
from Utils.correct_time_offset import correctTimeOffset


def scrapeArticles(targetNumWeek):
    siteTitle = 'Coinbase Archive'
    print('--> ' + siteTitle)
    
    url = 'https://www.coinbase.com/bytes/archive?page='
    print(f'> {url}')
    delay = 3
    dateFormat = '%b %d, %Y'
    isEnough = True

    postPath = 'a[class="DesktopArchiveArticle__StyledLink-sc-1ww2hte-0 bwTULY"]'
    postTitlePath = 'p[class="cds-typographyResets-t1xhpuq2 cds-headline-hb7l4gg cds-foreground-f1yzxzgu cds-transition-txjiwsi cds-start-s1muvu8a cds-1-_9w3lns"]'
    # postUrlPath = 'a'
    postDatePath = 'p[class="cds-typographyResets-t1xhpuq2 cds-label1-ln29cth cds-foregroundMuted-f1vw1sy6 cds-transition-txjiwsi cds-start-s1muvu8a cds-6-_1ts70zl"]'
    adCloseBtnPath = 'button[class="BytesSignupModal__StyledButton-sc-1x4h11y-2 eDiIyn"]'
    
    service = Service(ChromeDriverManager().install())
    options = create_option(headless=False)
    driver = webdriver.Chrome(options=options, service=service)
    curPg = 1
    isEnough = False
    isAdClosed = False
    dataList = []
    
    urlFull = url + str(curPg)
    driver.get(urlFull)
    driver.minimize_window()
    time.sleep(4)
    
    while (curPg <= 13):
        if not isAdClosed:
            try: 
                WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.CSS_SELECTOR, adCloseBtnPath))).click()
                time.sleep(2)
                isAdClosed = True
                print('ad close btn found :)')
            except Exception as err: 
                print('ad close button not found')
        
        posts = driver.find_elements(By.CSS_SELECTOR, postPath)
        for post in posts:
            postTitle = post.find_element(By.CSS_SELECTOR, postTitlePath).text
            postUrl = post.get_attribute('href')
            postDate = post.find_element(By.CSS_SELECTOR, postDatePath).text
            
            if (postDate == ''):
                print('> err: blank page, pls try again')
                return
                # continue
            postDate = postDate.split(' ')
            if len(postDate[1]) == 2:
                postDate[1] = '0' + postDate[1]
            postDate = ' '.join(postDate)
            
            if not correctTimeOffset(postDate, dateFormat, targetNumWeek):
                print('+ enough post')
                isEnough = True
                break
            
            postDate = datetime.strftime(datetime.strptime(postDate, dateFormat), outputDateFormat)
            dataRow = [postDate, postTitle, postUrl]
            dataList.append(dataRow)
            # print(dataRow)
            
        if isEnough:
            print('> done\n')
            writeScrapedData(siteTitle, fileName, dataList, targetNumWeek, url)
            driver.quit()
            break
        
        print('+ still searching')
        curPg += 1
        pgBtnPath = f'a[href="/bytes/archive?page={curPg}"]'
        driver.execute_script("arguments[0].click();", driver.find_element(By.CSS_SELECTOR, pgBtnPath))
        time.sleep(3)
        