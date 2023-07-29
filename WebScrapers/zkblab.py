from selenium import webdriver
from selenium.webdriver.common.by import By
from datetime import datetime, time
import time
# from Utils.error_handler import handle_scrape_errors
from Utils.driver_options import create_option
from Utils.write_to_list import writeScrapedData
from Utils.correct_time_offset import correctTimeOffset
from globals import fileName, outputDateFormat


# @handle_scrape_errors()
def scrapeZkblab(targetNumWeek):
    print('@zkblab')
    stopSign = 'Nothing here'
    page = 1
    delay = 1.5
    dateFormat = "%d %B %Y"

    pageUrl = 'https://zkplabs.network/blog?page='
    pathLink = "//a[contains(@class,'chakra-link css-spn4bz') and h2]"

    # driver = webdriver.Chrome()
    driver = webdriver.Chrome(options=create_option())

    dataList = []
    isEnough = False
    while True:
        driver.get(pageUrl + str(page))
        time.sleep(delay)

        body = driver.find_element(By.TAG_NAME, 'body')
        if (stopSign in body.text):
            print('* Dead end')
            break

        pathLink = "//a[contains(@class,'chakra-link css-spn4bz') and h2]"
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
    writeScrapedData('ZKP Lab', fileName, dataList, targetNumWeek)
    # with open(fileName, 'a', encoding='UTF8') as file:
    #     writer = csv.writer(file)

    #     writer.writerow(['=== ZKP LAB ==='])
    #     for data in dataList:
    #         writer.writerow(data)
    #     writer.writerow([])

    print('> done')
    driver.quit()
