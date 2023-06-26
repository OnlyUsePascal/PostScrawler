from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from datetime import datetime, timedelta
import time
import csv

fileName = 'test.csv'

# all of functions for scraping here



def scrapeZkblab(targetNumWeek):
    print('getting zkblab')    
    url = ''
    # some code here


def scrapeGfi(targetNumWeek):
    print('getting gfi blockchain')    
    url = 'https://gfiblockchain.com/bai-viet-moi-nhat-tu-gfs.html'
    numScroll = 5
    delayScroll = 1.2
    dateFormat = "%d/%m/%Y"
    curLen = 0

    driver = webdriver.Chrome()
    driver.get(url)

    body = driver.find_element(By.TAG_NAME, "body")
    for _ in range(numScroll):
        pathHeader = "//h3[@class='jeg_post_title']"
        headers = driver.find_elements(By.XPATH, pathHeader)

        pathTime = "//div[@class='jeg_meta_date']"
        dates = driver.find_elements(By.XPATH, pathTime)
        
        if (len(headers) == curLen):
            print('no new posts')
            break

        # finding approriate post
        isEnough = False
        dataList = []
        for i in range (len(headers)):
            publishedTime = datetime.strptime(dates[i].text, dateFormat)
            timeDiff = datetime.now() - publishedTime

            timeRow = publishedTime.strftime('%Y-%m-%d')
            headerRow = headers[i].text
            urlRow = headers[i].find_element(By.TAG_NAME, 'a').get_attribute('href')
            
            # print(timeRow, headerRow)

            if (timeDiff > timedelta(weeks=targetNumWeek)):
                print('enough posts')
                isEnough = True
                break
            
            dataList.append([timeRow, headerRow, urlRow])


        if (isEnough):
            # start listing
            with open(fileName, 'a', encoding='UTF8') as  file:
                writer = csv.writer(file)

                writer.writerow(['=== GFI ==='])
                for data in dataList:
                    writer.writerow(data)
            break
            
        body.send_keys(Keys.PAGE_DOWN)
        print('scrolled =====')
        time.sleep(delayScroll)

    print('> done')
    driver.quit()


# everything start here
def webscrape(targetNumWeek = 1):
    #reset 
    with open(fileName, 'w') as file:
        file.flush()

    #zkplab
    scrapeZkblab(targetNumWeek)

    #gfi   
    scrapeGfi(targetNumWeek)

webscrape(1)


