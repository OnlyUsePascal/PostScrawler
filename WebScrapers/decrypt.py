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
def scrapeDecrypt(targetNumWeek):
    print('Starting scraping Decrypt...')
    pageUrl = 'https://decrypt.co/news/technology'
    isWithinSearchWeek = True
    driver = webdriver.Chrome(options=create_option())
    driver.get(pageUrl)
    blogs_list = []

    while (isWithinSearchWeek):
        # Wait until all blogs are presented on the web
        try:
            articles = WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'main > div > div:last-child > div > article > article')))
        except TimeoutException:
            print('Loading take too long')
            break
        # Get last post's date
        last_article_date = articles[-1].find_element(By.CSS_SELECTOR, 'div:first-child > h4').text
        last_article_date = datetime.strptime(last_article_date, '%b %d, %Y')

        # Check for the last post's published date, if within the target week, keep loading more contents
        if (datetime.now() - last_article_date) > timedelta(weeks=targetNumWeek):
            # First article session
            def scrapeFirstSession():
                try:
                    first_article = driver.find_element(By.CSS_SELECTOR, 'main > div > article > div > div > div:first-child > article > div:last-child')
                except Exception:
                    print("First article session not avaiable")
                    return
                # print(first_article.text)
                title = first_article.find_element(By.CSS_SELECTOR, 'div a.linkbox__overlay').get_attribute('innerText')
                date = first_article.find_element(By.CSS_SELECTOR, 'div footer > div:first-child time:first-child').text
                date = datetime.strptime(date, '%b %d, %Y')
                link = first_article.find_element(By.CSS_SELECTOR, 'div a.linkbox__overlay').get_attribute('href')
                if (datetime.now() - date) > timedelta(weeks=targetNumWeek):
                    # Return True when enough post so that it can stop the loop
                    return True
                blogs_list.append([date.strftime(outputDateFormat), title, link])

            if scrapeFirstSession():
                break

            # Second article session
            def scrapeSecondSession():
                try:
                    second_articles = driver.find_elements(By.CSS_SELECTOR, 'main > div > article > div > div > div:not(:first-child) div.grow')
                except Exception:
                    print("Second article session not avaiable")
                    return
                for article in second_articles:
                    title = article.find_element(By.CSS_SELECTOR, 'div a.linkbox__overlay').get_attribute('innerText')
                    date = article.find_element(By.CSS_SELECTOR, 'div footer > div:first-child time:first-child').text
                    date = datetime.strptime(date, '%b %d, %Y')
                    link = article.find_element(By.CSS_SELECTOR, 'div a.linkbox__overlay').get_attribute('href')
                    if (datetime.now() - date) > timedelta(weeks=targetNumWeek):
                        # Return True when enough post so that it can stop the loop
                        return True
                    blogs_list.append([date.strftime(outputDateFormat), title, link])

            if scrapeSecondSession():
                break

            # Third article session
            def scrapeThirdSession():
                if not articles:
                    print("Third article session not avaiable")
                    return

                for article in articles:
                    title = article.find_element(By.CSS_SELECTOR, 'div:last-child article h3 span').text
                    date = datetime.strptime(article.find_element(By.CSS_SELECTOR, 'div:first-child > h4').text, '%b %d, %Y')
                    link = article.find_element(By.CSS_SELECTOR, 'div:last-child article h3 a').get_attribute('href')
                    if (datetime.now() - date) > timedelta(weeks=targetNumWeek):
                        # Return True when enough post so that it can stop the loop
                        return True
                    blogs_list.append([date.strftime(outputDateFormat), title, link])

            if scrapeThirdSession():
                break

            break

        # Load more stories
        load_more_btn = driver.find_element(By.CSS_SELECTOR, 'main > div > div:last-child > div > article button')
        load_more_btn.send_keys(Keys.ENTER)

    # Write data into file
    writeScrapedData('Decrypt', fileName, blogs_list, targetNumWeek)
    print('Scraping Decrypt Finished')
    driver.quit()
