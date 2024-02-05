import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from datetime import datetime
from Utils.driver_options import create_option
from Utils.write_to_list import writeScrapedData
from Utils.correct_time_offset import correctTimeOffset
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from globals import fileName, outputDateFormat


def scrapeVitalik(targetNumWeek):
    print('@Vitalik')
    pageUrl = 'https://vitalik.eth.limo/'
    dateFormat = '%Y %b %d'

    # driver = webdriver.Chrome()
    driver = webdriver.Chrome(options=create_option(), service=Service(ChromeDriverManager().install()))
    driver.get(pageUrl)

    posts = driver.find_elements(By.TAG_NAME, 'li')
    dataList = []
    for post in posts:
        postDate = post.find_element(By.TAG_NAME, 'span').text
        postTitle = post.find_element(By.TAG_NAME, 'a').text
        postUrl = post.find_element(By.TAG_NAME, 'a').get_attribute('href')

        if not correctTimeOffset(postDate, dateFormat, targetNumWeek):
            print('* enough post')
            break

        postDate = datetime.strftime(datetime.strptime(postDate, dateFormat), outputDateFormat)
        dataRow = [postDate, postTitle, postUrl]
        # print(dataRow)
        dataList.append(dataRow)
        
    writeScrapedData('Vitalik', fileName, dataList, targetNumWeek)
    print('> done')
    driver.quit()
