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
def scrapeCoinDesk(targetNumWeek):
    print('Starting scraping Coin Desk...')
    pageUrl = 'https://www.coindesk.com/tech/'
    isWithinSearchWeek = True
    driver = webdriver.Chrome(options=create_option())
    driver.get(pageUrl)
    blogs_list = []

    while (isWithinSearchWeek):
        # Wait until all blogs are presented on the web
        try:
            articles = WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.articles-wrapper div.article-cardstyles__StyledWrapper-q1x8lc-0 div.article-cardstyles__AcTitle-q1x8lc-1')))
        except TimeoutException:
            print('Loading take too long')
            break
        # Get last post's date
        last_article_date = articles[-1].find_element(By.CSS_SELECTOR, 'div.timing-data div.display-desktop-block > span').text
        last_article_date = datetime.strptime(last_article_date, '%b %d, %Y')

        # Check for the last post's published date, if within the target week, keep loading more contents
        if (datetime.now() - last_article_date) > timedelta(weeks=targetNumWeek):
            for article in articles:
                title = article.find_element(By.CSS_SELECTOR, 'h5 > a.card-title').text
                date = datetime.strptime(article.find_element(By.CSS_SELECTOR, 'div.timing-data div.display-desktop-block > span').text, '%b %d, %Y')
                link = article.find_element(By.CSS_SELECTOR, 'h5 > a').get_attribute('href')
                if (datetime.now() - date) > timedelta(weeks=targetNumWeek):
                    isWithinSearchWeek = False
                    break
                blogs_list.append([date.strftime(outputDateFormat), title, link])
            break

        # Load more stories
        load_more_btn = driver.find_element(By.CSS_SELECTOR, 'div.button-holder button.Button__ButtonBase-sc-1sh00b8-0')
        load_more_btn.send_keys(Keys.ENTER)

    # Write data into file
    writeScrapedData('Coin Desk', fileName, blogs_list, targetNumWeek)
    print('Scraping Coin Desk Finished')
    driver.quit()
