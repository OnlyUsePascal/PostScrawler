from selenium import webdriver
from selenium.webdriver.common.by import By
from datetime import datetime, time
from Utils.driver_options import create_option
from Utils.write_to_list import writeScrapedData
from Utils.correct_time_offset import correctTimeOffset
from globals import fileName, outputDateFormat


def scrapeApple(targetNumWeek):
    print('@apple')
    pageUrl = 'https://www.apple.com/au/newsroom/archive/?page='
    page = 1
    delay = 1.2
    dateFormat = "%d %B %Y"

    postPath = "//a[@class='result__item row-anchor']"

    # driver = webdriver.Chrome()
    driver = webdriver.Chrome(options=create_option())

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

    writeScrapedData('Apple', fileName, dataList, targetNumWeek)
    # with open(fileName, 'a', encoding='UTF8') as file:
    #     writer = csv.writer(file)

    #     writer.writerow(['=== Apple ==='])
    #     for data in dataList:
    #         writer.writerow(data)
    #     writer.writerow([])

    print('> done')
    driver.quit()
