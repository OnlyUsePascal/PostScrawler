import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from datetime import datetime
from Utils.driver_options import create_option
from Utils.write_to_list import writeScrapedData
from Utils.correct_time_offset import correctTimeOffset
from globals import fileName, outputDateFormat
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC


def scrapeBankless(targetNumWeek):
    print('@Bankless')
    pageUrl = 'https://www.bankless.com/read'
    dateFormat = "%b %d, %Y"
    # page = 1

    # driver = webdriver.Chrome()
    driver = webdriver.Chrome(options=create_option())
    driver.get(pageUrl)

    postPath = "//a[@class='item articleBlockSmall']"
    postTitlePath = "h1[class='wow fadeInUp']"
    postDatePath = "div[class='meta wow fadeInUp'] span"

    dataList = []
    isEnough = False
    try:
        while True:
            posts = driver.find_elements(By.XPATH, postPath)
            for post in posts:
                postUrl = post.get_attribute('href')

                # open in new tab
                driver.execute_script(f'window.open("{postUrl}","_blank");')
                driver.switch_to.window(driver.window_handles[1])
                time.sleep(4)

                postTitle = driver.find_element(By.CSS_SELECTOR, postTitlePath).text
                postDate = driver.find_elements(By.CSS_SELECTOR, postDatePath)[1].text.split(' ')
                if len(postDate[1]) == 2:
                    postDate[1] = '0' + postDate[1]
                postDate = ' '.join(postDate)

                if not correctTimeOffset(postDate, dateFormat, targetNumWeek):
                    print("* enough posts")
                    isEnough = True
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                    break

                postDate = datetime.strftime(datetime.strptime(postDate, dateFormat), outputDateFormat)
                dataRow = [postDate, postTitle, postUrl]
                print(dataRow)
                dataList.append(dataRow)

                # close tab + switch to base
                driver.close()
                driver.switch_to.window(driver.window_handles[0])

            if (isEnough):
                break

            print("* still searching")

            # load more btn
            btnPath = "a[class='loadMoreFilterBtn']"
            btn = driver.find_element(By.CSS_SELECTOR, btnPath)
            driver.execute_script("arguments[0].click();", btn)
            time.sleep(2)
    except Exception as err:
        print(err)
    
    writeScrapedData('Bankless', fileName, dataList, targetNumWeek)
    print('> done')
    driver.quit()
