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
def scrapeAlchemyBlog(targetNumWeek):
    print('Starting scraping Alchemy Blog...')
    pageUrl = 'https://www.alchemy.com/blog'
    isWithinSearchWeek = True
    driver = webdriver.Chrome(options=create_option())
    driver.get(pageUrl)
    blogs_list = []

    while (isWithinSearchWeek):
        # Wait until all blogs are presented on the web
        try:
            blog_links = WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.collection-list.w-clearfix.w-dyn-items.w-row > div > div.thumbnail-wrapper > a')))
        except TimeoutException:
            print('Loading take too long')
            break
        # Check for last blog's date
        driver.execute_script(f'window.open("{blog_links[-1].get_attribute("href")}","_blank");')
        driver.switch_to.window(driver.window_handles[1])

        date = datetime.strptime(driver.find_element(By.CSS_SELECTOR, 'div.blog-date').text, '%B %d, %Y')
        if (datetime.now() - date) < timedelta(weeks=targetNumWeek):
            driver.switch_to.window(driver.window_handles[0])

            # Load more button
            # If last post's date is within search week, search more. Else start scraping
            load_more_btn = driver.find_element(By.CSS_SELECTOR, 'div[role="navigation"] a[aria-label="Next Page"]')
            load_more_btn.send_keys(Keys.ENTER)

            # Close tab after done checking
            driver.switch_to.window(driver.window_handles[1])
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            continue

        for blog_link in blog_links:
            # Close tab after done scraping
            # This also close tab that was opened in the prev session
            driver.close()
            driver.switch_to.window(driver.window_handles[0])

            # Open link in new tab
            driver.execute_script(f'window.open("{blog_link.get_attribute("href")}","_blank");')
            driver.switch_to.window(driver.window_handles[1])

            title = driver.find_element(By.CSS_SELECTOR, 'h1.blog-post-title').text
            date = datetime.strptime(driver.find_element(By.CSS_SELECTOR, 'div.blog-date').text, '%B %d, %Y')
            link = driver.current_url
            if (datetime.now() - date) > timedelta(weeks=targetNumWeek):
                isWithinSearchWeek = False
                break
            blogs_list.append([date.strftime(outputDateFormat), title, link])

            # Close tab after done scraping
            # driver.close()
            # driver.switch_to.window(driver.window_handles[0])
        break

    # Write data into file
    writeScrapedData('Alchemy Blog', fileName, blogs_list, targetNumWeek)
    print('Scraping Alchemy Blog Finished')
    driver.quit()
