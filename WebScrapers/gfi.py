from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from datetime import datetime, time, timedelta
from Utils.driver_options import create_option
from Utils.write_to_list import writeScrapedData
# from Utils.correct_time_offset import correctTimeOffset
from globals import fileName, outputDateFormat


def scrapeGfi(targetNumWeek):
    print('@getting gfi blockchain')
    url = 'https://gfiblockchain.com/bai-viet-moi-nhat-tu-gfs.html'
    # numScroll = 5
    delayScroll = 1.2
    dateFormat = "%d/%m/%Y"
    curLen = 0

    # driver = webdriver.Chrome()
    driver = webdriver.Chrome(options=create_option())
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
        for i in range(len(headers)):
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
            writeScrapedData('GFI', fileName, dataList, targetNumWeek)
            break

        body.send_keys(Keys.PAGE_DOWN)
        print('* still searching')
        time.sleep(delayScroll)

    print('> done')
    driver.quit()
