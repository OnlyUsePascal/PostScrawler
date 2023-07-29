from selenium import webdriver
from selenium.webdriver.common.by import By
from datetime import datetime
from Utils.driver_options import create_option
from Utils.write_to_list import writeScrapedData
from Utils.correct_time_offset import correctTimeOffset
from globals import fileName, outputDateFormat
import time


def scrapeAliAbdaal(targetNumWeek):
    print('@Ali Abdaal')
    url = "https://aliabdaal.com/articles/page/"
    page = 1
    delay = 1.2
    dateFormat = '%B %d, %Y'
    isEnough = False

    postPath = '//div[@style="box-shadow: rgba(149, 157, 165, 0.2) 0px 8px 24px;"]'

    # driver = webdriver.Chrome()
    driver = webdriver.Chrome(options=create_option())

    dataList = []
    while page <= 3:
        driver.get(url + str(page) + '/')
        time.sleep(delay)

        posts = driver.find_elements(By.XPATH, postPath)
        for post in posts:
            postUrl = post.find_element(By.TAG_NAME, 'a').get_attribute('href')
            postTitle = post.find_element(By.TAG_NAME, 'h3').text
            postTime = post.find_elements(By.TAG_NAME, 'h4')[1].text

            timeTxt = datetime.strftime(datetime.strptime(postTime, dateFormat), outputDateFormat)
            dataRow = [timeTxt, postTitle, postUrl]
            # print(dataRow)

            if not correctTimeOffset(postTime, dateFormat, targetNumWeek):
                print('* enough post')
                isEnough = True
                break

            dataList.append(dataRow)

        if isEnough:
            break

        page += 1
        print('* still searching')

    writeScrapedData('Ali Abdaal', fileName, dataList, targetNumWeek)
    print('> done')
    driver.quit()
