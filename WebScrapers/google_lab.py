from selenium import webdriver
from selenium.webdriver.common.by import By
from datetime import time
from Utils.driver_options import create_option
from Utils.write_to_list import writeScrapedData
from Utils.correct_time_offset import correctTimeOffset
from globals import fileName
import time


def scrapeGoogleLab(targetNumWeek):
    print('@google lab')
    delay = 1.5
    url = 'https://blog.google/technology/developers/'
    dateFormat = '%Y-%m-%d'
    isEnough = False

    btnPath = "//button[@class='article-list__load-more--cards js-load-more-button']"
    # path2 = "//span[@class='article-list__loader-text']"
    postPath = "//div[@class='feed-article ng-scope']"
    # datePath = "//span[@class='eyebrow__date]"

    # driver = webdriver.Chrome()
    driver = webdriver.Chrome(options=create_option())

    # site = driver.get(url)
    driver.get(url)
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

                dataRow = [date, title, url]

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

        writeScrapedData('Google lab', fileName, dataList, targetNumWeek)
        # with open(fileName, 'a', encoding='UTF8') as  file:
        #     writer = csv.writer(file)

        #     writer.writerow(['=== GoogleLab ==='])
        #     for data in dataList:
        #         writer.writerow(data)
        #     writer.writerow([])

    except Exception as err:
        print(err)

    print('> done')
    driver.quit()
