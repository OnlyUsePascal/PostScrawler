from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from datetime import datetime, timedelta
from Utils.error_handler import handle_scrape_errors
from Utils.driver_options import create_option
from Utils.write_to_list import writeScrapedData
from globals import fileName, outputDateFormat


@handle_scrape_errors
def scrapeCointelegraph(targetNumWeek):
    print('Starting scraping Cointelegraph...')
    pageUrl = 'https://cointelegraph.com/'
    isWithinSearchWeek = True
    driver = webdriver.Chrome(options=create_option())
    driver.get(pageUrl)
    blogs_list = []

    while (isWithinSearchWeek):
        # Wait until all blogs are presented on the web
        try:
            articles = WebDriverWait(driver, 10).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, 'ul.posts-listing__list > li.posts-listing__item')))
        except TimeoutException:
            print('Loading take too long')
            break
        # Get last post's date
        try:
            last_article_date = articles[-1].find_element(By.CSS_SELECTOR, 'div time').get_attribute('innerText')
            last_article_date = datetime.strptime(last_article_date, '%b %d, %Y')
        except StaleElementReferenceException:
            continue
        except Exception:
            last_article_date = datetime.now()
        # print(last_article_date)

        # Check for the last post's published date, if within the target week, keep loading more contents
        if (datetime.now() - last_article_date) > timedelta(weeks=targetNumWeek):
            for article in articles:
                # skip if target has this class
                if 'posts-listing__item_triple' in article.get_attribute('class').split():
                    continue

                # Some posts are empty thus causing bugs
                try:
                    title = article.find_element(By.CSS_SELECTOR, 'header.post-card__header span.post-card__title').get_attribute('innerText')
                    link = article.find_element(By.CSS_SELECTOR, 'header.post-card__header > a.post-card__title-link').get_attribute('href')
                except Exception:
                    continue

                # Get date, return today if it was posted n times ago
                try:
                    date = datetime.strptime(article.find_element(By.CSS_SELECTOR, 'div time').get_attribute('innerText'), '%b %d, %Y')
                except Exception:
                    date = datetime.now()

                if (datetime.now() - date) > timedelta(weeks=targetNumWeek):
                    isWithinSearchWeek = False
                    break
                blogs_list.append([date.strftime(outputDateFormat), title, link])
            break

        # Scroll down to bottom to load more articles
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight-100);")
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_UP)

    # Write data into file
    writeScrapedData('Cointelegraph', fileName, blogs_list, targetNumWeek)
    print('Scraping Cointelegraph Finished')
    driver.quit()
