from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from datetime import datetime, time
from Utils.driver_options import create_option
# from Utils.write_to_list import writeScrapedData
from Utils.correct_time_offset import correctTimeOffset
from globals import fileName, outputDateFormat
import csv


def scrapeCoin98(targetNumWeek):
    print('@Coin98')
    pageUrlBase = 'https://coin98.net/posts/title/'
    pageUrlEnds = [
        'buidl',
        'research',
        'invest',
        'he-sinh-thai',
        'regulation'
    ]
    dateFormat = '%d %b, %Y'

    postPath = 'div.style_cardInsight__F9av_'
    postUrlPath = 'a.style_no-underline__FM_LN'
    postTitlePath = 'div.card-post-title'
    postDatePath = 'div.card-time span'
    # driver = webdriver.Chrome()
    driver = webdriver.Chrome(options=create_option())

    with open(fileName, 'a', encoding='UTF8') as file:
        writer = csv.writer(file)
        writer.writerow(['=== Coin98 ==='])

    # for each endpoint
    for pageUrlEnd in pageUrlEnds:
        print(f'> {pageUrlEnd}')
        pageUrl = pageUrlBase + pageUrlEnd
        driver.get(pageUrl)
        time.sleep(2)

        # start scan
        dataList = []
        isEnough = False
        while True:
            posts = driver.find_elements(By.CSS_SELECTOR, postPath)
            for post in posts:
                postUrl = post.find_element(By.CSS_SELECTOR, postUrlPath).get_attribute('href')
                postTitle = post.find_element(By.CSS_SELECTOR, postTitlePath).text
                postDate = post.find_element(By.CSS_SELECTOR, postDatePath).text

                # ignore very recent post
                # print(postDate)
                if ('ago' in postDate):
                    continue

                if not correctTimeOffset(postDate, dateFormat, targetNumWeek):
                    print('* enough post')
                    isEnough = True
                    break

                postDate = datetime.strftime(datetime.strptime(postDate, dateFormat), outputDateFormat)
                dataRow = [postDate, postTitle, postUrl]
                dataList.append(dataRow)

            if (isEnough):
                break

            driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)
            time.sleep(2)

        # write to file
        with open(fileName, 'a', encoding='UTF8') as file:
            writer = csv.writer(file)

            writer.writerow([f'> {pageUrlEnd}'])
            if len(dataList) == 0:
                writer.writerow([f'No articles/blogs were found within {targetNumWeek} weeks'])
            else:
                for data in dataList:
                    writer.writerow(data)
            writer.writerow([])

    print('> done')
    driver.quit()
