from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from datetime import datetime, timedelta
from Utils.error_handler import handle_scrape_errors
from Utils.driver_options import create_option
from Utils.write_to_list import writeScrapedData
from globals import fileName, outputDateFormat


@handle_scrape_errors
def scrapeDevelopersArchives(targetNumWeek):
    print('Starting scraping Developers Archives...')
    pageUrl = 'https://pages.near.org/blog/category/developers/'
    isWithinSearchWeek = True
    driver = webdriver.Chrome(options=create_option())
    driver.get(pageUrl)
    blogs_list = []

    while (isWithinSearchWeek):
        try:
            blogs = WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'main > div > nr-section > div:nth-child(2) > div:first-child > div > div:nth-child(2)')))
        except TimeoutException:
            print('Loading take too long')
            break

        for blog in blogs:
            title = blog.find_element(By.CSS_SELECTOR, 'p > a').get_attribute('innerText')
            date = datetime.strptime(blog.find_element(By.CSS_SELECTOR, 'div:first-child > div:nth-child(2)').get_attribute('innerText'), '%B %d, %Y')
            link = blog.find_element(By.CSS_SELECTOR, 'p > a').get_attribute('href')
            if (datetime.now() - date) > timedelta(weeks=targetNumWeek):
                isWithinSearchWeek = False
                break
            blogs_list.append([date.strftime(outputDateFormat), title, link])

        # Next page button
        next_page_btn = driver.find_element(By.CSS_SELECTOR, 'nav > ul.page-numbers > li:last-child > a')
        next_page_btn.send_keys(Keys.ENTER)

        # Closing old tab (as it opens a new window) and redirect to new tab
        driver.close()
        driver.switch_to.window(driver.window_handles[0])

    # Write data into file
    writeScrapedData('Developers Archives', fileName, blogs_list, targetNumWeek)
    print('Scraping Developers Archives Finished')
    driver.quit()
