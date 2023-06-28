from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from datetime import datetime, timedelta
from xvfbwrapper import Xvfb
import time
import csv

fileName = 'test.csv'
outputDateFormat = '%Y-%m-%d'

def correctTimeOffset(inputDate, dateFormat, targetNumWeek):
    publishedTime = datetime.strptime(inputDate, dateFormat)
    timeDiff = datetime.now() - publishedTime
    # print(timeDiff.days)
    return timeDiff <= timedelta(weeks=targetNumWeek)


# all websites here
def scrapeZkblab(targetNumWeek):
    print('@zkblab')    
    stopSign = 'Nothing here'
    page = 1
    delay = 1.5
    dateFormat = "%d %B %Y"
    
    pageUrl = 'https://zkplabs.network/blog?page='
    pathLink = "//a[contains(@class,'chakra-link css-spn4bz') and h2]"

    driver = webdriver.Chrome()

    dataList = [] 
    isEnough = False
    while True:
        driver.get(pageUrl + str(page))
        time.sleep(delay)

        body = driver.find_element(By.TAG_NAME, 'body')        
        if (stopSign in body.text):
            print('* Dead end')
            break
        
        linkList = body.find_elements(By.XPATH, pathLink)

        for link in linkList:
            date = link.find_element(By.TAG_NAME, 'div').text
            title = link.find_element(By.TAG_NAME, 'h2').text
            url = link.get_attribute('href')

            dateTxt = datetime.strftime(datetime.strptime(date, dateFormat), outputDateFormat)
            dataRow = [dateTxt, title, url]

            status = correctTimeOffset(date, dateFormat, targetNumWeek)
            if (not status):
                print('* enough posts')
                isEnough = True
                break

            dataList.append(dataRow)
        
        if (isEnough):
            break

        print('* still searching')
        page += 1
    
    # write to file
    with open(fileName, 'a', encoding='UTF8') as  file:
        writer = csv.writer(file)

        writer.writerow(['=== FKPLAB ==='])
        for data in dataList:
            writer.writerow(data)
        writer.writerow([])
        
    print('> done')
    driver.quit()


def scrapeGoogleLab(targetNumWeek):
    print('@google lab')
    delay = 1.5
    url = 'https://blog.google/technology/developers/'
    dateFormat = '%Y-%m-%d'
    isEnough = False

    btnPath = "//button[@class='article-list__load-more--cards js-load-more-button']" 
    path2 = "//span[@class='article-list__loader-text']"
    postPath = "//div[@class='feed-article ng-scope']"
    datePath = "//span[@class='eyebrow__date]"

    driver = webdriver.Chrome() 
    site = driver.get(url)
    time.sleep(delay)

    try:
        dataList = []

        btn = driver.find_element(By.XPATH, btnPath)
        while True:
            newPosts = driver.find_elements(By.XPATH, postPath)

            for post in newPosts[-6:]:
                date = post.find_element(By.TAG_NAME, 'time').get_attribute('datetime')[:10]
                title = post.find_element(By.TAG_NAME, 'h3').text
                url = post.find_element(By.TAG_NAME, 'a').get_attribute('href')

                dataRow = [date,title,url]

                status = correctTimeOffset(str(date), dateFormat, targetNumWeek)
                if (not status):
                    print('* enough post')
                    isEnough = True
                    break
                    
                dataList.append(dataRow)

            if (isEnough):
                break

            print('* still searching')
            # reset btn
            btn = driver.find_element(By.XPATH, btnPath)
            driver.execute_script("arguments[0].click();", btn)
            time.sleep(delay)

        with open(fileName, 'a', encoding='UTF8') as  file:
            writer = csv.writer(file)

            writer.writerow(['=== GoogleLab ==='])
            for data in dataList:
                writer.writerow(data)
            writer.writerow([])

    except Exception as err:
        print(err)

    print('> done')
    driver.quit()


def scrapeApple(targetNumWeek):
    print('@apple')
    pageUrl = 'https://www.apple.com/au/newsroom/archive/?page='
    page = 1
    delay = 1.2
    dateFormat = "%d %B %Y"
    
    postPath = "//a[@class='result__item row-anchor']"

    driver = webdriver.Chrome()
    
    dataList = []
    isEnough = False
    while True:
        driver.get(pageUrl + str(page))
        time.sleep(delay)

        posts = driver.find_elements(By.XPATH, postPath)
        for post in posts:
            url = post.get_attribute('href')
            metadata = post.get_attribute('aria-label').split(' - ')
            date = metadata[0]
            title = metadata[2]

            dateTxt = datetime.strftime(datetime.strptime(date, dateFormat), outputDateFormat)
            dataRow = [dateTxt, title, url]
            # print(dataRow)

            if not correctTimeOffset(date, dateFormat, targetNumWeek):
                print('* enough post')
                isEnough = True
                break 

            dataList.append(dataRow)
        
        if isEnough:
            break

        print('* keep searching')
        page += 1
    
    with open(fileName, 'a', encoding='UTF8') as  file:
        writer = csv.writer(file)

        writer.writerow(['=== Apple ==='])
        for data in dataList:
            writer.writerow(data)
        writer.writerow([])

    print('> done')
    driver.quit()
    

def scrapeForteLab(targetNumWeek):
    print('@fortelab')
    pageUrl = 'https://fortelabs.com/blog/?page='
    page = 1
    delay = 1.2
    dateFormat = "%B %d, %Y"
    
    postPath = "//h3[@class='elementor-post__title']"

    driver = webdriver.Chrome()
    
    dataList = []
    isEnough = False
    while page <= 5:
        driver.get(pageUrl + str(page))
        time.sleep(delay)

        postUrls = driver.find_elements(By.XPATH, postPath)
        postPageList = []

        # get post url list
        for post in postUrls:
            postUrl = post.find_element(By.TAG_NAME, 'a').get_attribute('href')
            postPageList.append(postUrl)

        # retrieve data by each post page
        for postUrl in postPageList:
            driver.get(postUrl)
            timePath = "//span[@class='elementor-icon-list-text elementor-post-info__item elementor-post-info__item--type-custom']"
            titlePath = "//h1[@class='elementor-heading-title elementor-size-default']"
            
            date = driver.find_elements(By.XPATH, timePath)[-1].text
            title = driver.find_element(By.XPATH, titlePath).text

            dateTxt = datetime.strftime(datetime.strptime(date, dateFormat), outputDateFormat)
            dataRow = [dateTxt, title, postUrl]
            # print(dataRow)

            if not correctTimeOffset(date, dateFormat, targetNumWeek):
                print('* enough post')
                isEnough = True
                break 

            dataList.append(dataRow)
        
        if isEnough:
            break

        print('* keep searching')
        page += 1
    
    with open(fileName, 'a', encoding='UTF8') as  file:
        writer = csv.writer(file)

        writer.writerow(['=== ForteLab ==='])
        for data in dataList:
            writer.writerow(data)
        writer.writerow([])

    print('> done')
    driver.quit()


def scrapeGfi(targetNumWeek):
    print('@getting gfi blockchain')    
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
                print('* enough posts')
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
                writer.writerow([])
            break
            
        body.send_keys(Keys.PAGE_DOWN)
        print('* still searching')
        time.sleep(delayScroll)

    print('> done')
    driver.quit()


# everything start here
def webscrape(targetNumWeek = 1):
    #reset 
    with open(fileName, 'w') as file:
        file.flush()


    scrapeZkblab(targetNumWeek)
    # scrapeGoogleLab(targetNumWeek)
    # scrapeApple(targetNumWeek)
    # scrapeForteLab(targetNumWeek)
    # scrapeGfi(targetNumWeek)

display = Xvfb()
display.start()
webscrape(5)
display.stop()

