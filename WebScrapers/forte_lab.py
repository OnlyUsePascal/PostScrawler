from selenium import webdriver
from selenium.webdriver.common.by import By
from datetime import datetime, time
from Utils.driver_options import create_option
from Utils.write_to_list import writeScrapedData
from Utils.correct_time_offset import correctTimeOffset
from globals import fileName, outputDateFormat


def scrapeForteLab(targetNumWeek):
    print('@fortelab')
    pageUrl = 'https://fortelabs.com/blog/?page='
    page = 1
    delay = 1.2
    dateFormat = "%B %d, %Y"

    postPath = "//h3[@class='elementor-post__title']"

    # driver = webdriver.Chrome()
    driver = webdriver.Chrome(options=create_option())

    dataList = []
    isEnough = False
    while True:
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

    writeScrapedData('Forte Lab', fileName, dataList, targetNumWeek)
    print('> done')
    driver.quit()
