from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from datetime import datetime, timedelta
import time
import csv

fileName = 'test.csv'
outputDateFormat = '%Y-%m-%d'

# all of functions for scraping here



def scrapeZkblab(targetNumWeek):
    print('getting zkblab')    
    # targetNumWeek = 2
    pageUrl = 'https://zkplabs.network/blog?page='
    stopSign = 'Nothing here'
    page = 1
    delay = 1.5
    dateFormat = "%d %B %Y"

    driver = webdriver.Chrome()

    dataList = [] 
    isEnough = False
    while (page <= 6):
        driver.get(pageUrl + str(page))
        time.sleep(delay)

        body = driver.find_element(By.TAG_NAME, 'body')        
        if (stopSign in body.text):
            print('* Dead end')
            break
        
        pathLink = "//a[contains(@class,'chakra-link css-spn4bz') and h2]"
        linkList = body.find_elements(By.XPATH, pathLink)

        for link in linkList:
            publishedTime = datetime.strptime(link.find_element(By.TAG_NAME, 'div').text, dateFormat)
            title = link.find_element(By.TAG_NAME, 'h2').text
            url = link.get_attribute('href')

            # print(publishedTime.strftime(outputDateFormat))
            # print(datetime.now() - publishedTime)
            # print(title)
            # print(url)
            # print('====')

            timeDiff = datetime.now() - publishedTime
            if (timeDiff > timedelta(weeks=targetNumWeek)):
                print('* enough posts')
                isEnough = True
                break
            
            dataList.append([publishedTime.strftime(outputDateFormat), title, url])
        
        if (isEnough):
            break
        page += 1
    
    # write to file
    with open(fileName, 'a', encoding='UTF8') as  file:
        writer = csv.writer(file)

        writer.writerow(['=== FKPLAB ==='])
        for data in dataList:
            writer.writerow(data)

    print('> done')
    driver.quit()


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
    while True:
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

            timeRow = publishedTime.strftime(outputDateFormat)
            title = headers[i].text
            urlRow = headers[i].find_element(By.TAG_NAME, 'a').get_attribute('href')
            
            # print(timeRow, headerRow)

            if (timeDiff > timedelta(weeks=targetNumWeek)):
                print('enough posts')
                isEnough = True
                break
            
            dataList.append([timeRow, title, urlRow])


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

webscrape(2)


