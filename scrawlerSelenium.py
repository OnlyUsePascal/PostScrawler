from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from datetime import datetime, timedelta
from xvfbwrapper import Xvfb
import sys
import time
import csv

fileName = 'test.csv'
outputDateFormat = '%Y-%m-%d'


# Prevent Selenium from opening browser
# Selenium driver options
options = Options()
# options.add_argument('--headless')  # No window opened
options.add_experimental_option("excludeSwitches", ["enable-logging"])  # Disable logging
# options.add_argument("--log-level=3")
options.page_load_strategy = 'eager'


# Ultilities funtion
# check time correctness
def correctTimeOffset(inputDate, dateFormat, targetNumWeek):
    publishedTime = datetime.strptime(inputDate, dateFormat)
    timeDiff = datetime.now() - publishedTime
    # print(timeDiff.days)
    return timeDiff <= timedelta(weeks=targetNumWeek)

# write to list
def writeScrapedData(data_title: str, file, data_list: list, target_weeks):
    with open(file, 'a', encoding="utf-8") as file:
        writer = csv.writer(file)

        writer.writerow([f'=== {data_title} ==='])
        if not data_list:
            writer.writerow([f'No articles/blogs were found within {target_weeks} weeks'])
            return
        for data in data_list:
            writer.writerow(data)
        
        #blank separator
        writer.writerow([]) 

# Error handler
def handle_scrape_errors(func):
    """In cases where a website change their layout, it might break the code,
    this is used to prevent any errors that might break the whole program and instead keep running.

    Args:
        print_traceback (bool): whether to print traceback or not
    """
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as e:
            print(f'An error occured: {e}')
            print(f'{func.__name__} aborted')
        print('')  # Extra white space for readability
    return wrapper


# all of functions for scraping here
@handle_scrape_errors
def scrapeAcademyBinance(targetNumWeek):
    print('Starting scraping Academy Binance...')
    pageUrl = 'https://academy.binance.com/en/articles?page=1'
    delay = 1
    isWithinSearchWeek = True
    options.page_load_strategy = 'eager'
    driver = webdriver.Chrome(options=options)
    driver.get(pageUrl)
    blogs_list = []

    # Clear the filter bc there are bugs where the website open up with filter sometimes
    clear_filter_btn = driver.find_element(By.CSS_SELECTOR, 'button.css-1nkwl0a')
    clear_filter_btn.send_keys(Keys.ENTER)
    # Choose the list style cuz there are bugs with grid style
    list_layout_btn = driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Switch results to list layout"]')
    list_layout_btn.send_keys(Keys.ENTER)

    while (isWithinSearchWeek):
        blogs_title = driver.find_elements(By.CSS_SELECTOR, 'div.css-8qb8m4 h3.css-1ctqeuv')
        blogs_date = driver.find_elements(By.CSS_SELECTOR, 'div.css-fv3lde span.css-1sj28o2')
        blogs_link = driver.find_elements(By.CSS_SELECTOR, 'div.css-8qb8m4 > a')

        for i in range(len(blogs_title)):
            if (datetime.now() - datetime.strptime(blogs_date[i].text, '%b %d, %Y')) > timedelta(weeks=targetNumWeek):
                isWithinSearchWeek = False
                break
            date = datetime.strptime(blogs_date[i].text, '%b %d, %Y')
            blogs_list.append([date.strftime(outputDateFormat), blogs_title[i].text, blogs_link[i].get_attribute('href')])

        # Go to next page
        next_page_btn = driver.find_element(By.CSS_SELECTOR, 'a[aria-label="Go to next page"]')
        next_page_btn.send_keys(Keys.ENTER)
        time.sleep(delay)

    # Write data into file
    writeScrapedData('Academy Binance', fileName, blogs_list, targetNumWeek)
    print('Scraping Academy Binance Finished')
    driver.quit()


@handle_scrape_errors
def scrapeChainlink(targetNumWeek):
    print('Starting scraping Chainlink...')
    pageUrl = 'https://blog.chain.link/'
    isWithinSearchWeek = True
    options.page_load_strategy = 'none'
    driver = webdriver.Chrome(options=options)
    driver.get(pageUrl)
    blogs_list = []

    while (isWithinSearchWeek):
        # Wait until all blogs are presented on the web
        try:
            post_cards = WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.blog-post-bar div.post-card')))
        except TimeoutException:
            print('Loading take too long')
            break
        last_post_date = post_cards[-1].find_element(By.CSS_SELECTOR, 'span.post-date').text
        last_post_date = datetime.strptime(last_post_date, '%B %d, %Y')

        # Check for the last post's published date, if within the target week, keep loading more contents
        # else, start scraping contents
        if (datetime.now() - last_post_date) > timedelta(weeks=targetNumWeek):
            for post in post_cards:
                title = post.find_element(By.CSS_SELECTOR, 'div.post-title a').text
                date = datetime.strptime(post.find_element(By.CSS_SELECTOR, 'span.post-date').text, '%B %d, %Y')
                link = post.find_element(By.CSS_SELECTOR, 'div.post-title a').get_attribute('href')
                if (datetime.now() - date) > timedelta(weeks=targetNumWeek):
                    isWithinSearchWeek = False
                    break
                blogs_list.append([date.strftime(outputDateFormat), title, link])
            break

        # Load more contents
        load_more_btn = driver.find_element(By.CSS_SELECTOR, 'a.loadmore-btn')
        load_more_btn.send_keys(Keys.ENTER)

    # Write data into file
    writeScrapedData('Chainlink', fileName, blogs_list, targetNumWeek)
    print('Scraping Chainlink Finished')
    driver.quit()


@handle_scrape_errors
def scrapeOpenAI(targetNumWeek):
    print('Starting scraping OpenAI...')
    pageUrl = 'https://openai.com/blog'
    isWithinSearchWeek = True
    options.page_load_strategy = 'eager'
    driver = webdriver.Chrome(options=options)
    driver.get(pageUrl)
    blogs_list = []

    while (isWithinSearchWeek):
        # Wait until all blogs are presented on the web
        try:
            blogs = WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.ui-list ul.cols-container li')))
        except TimeoutException:
            print('Loading take too long')
            break
        for blog in blogs:
            title = blog.find_element(By.CSS_SELECTOR, 'div h3').text
            date = datetime.strptime(blog.find_element(By.CSS_SELECTOR, 'div span[aria-hidden="true"]').text, '%b %d, %Y')
            link = blog.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')
            if (datetime.now() - date) > timedelta(weeks=targetNumWeek):
                isWithinSearchWeek = False
                break
            blogs_list.append([date.strftime(outputDateFormat), title, link])

        next_page_btn = driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Next page"]')
        next_page_btn.send_keys(Keys.ENTER)

    # Write data into file

    writeScrapedData('OpenAI', fileName, blogs_list, targetNumWeek)
    print('Scraping OpenAI Finished')
    driver.quit()


@handle_scrape_errors
def scrapeGoogleBlogAI(targetNumWeek):
    print('Starting scraping Google Blog AI...')
    pageUrl = 'https://www.blog.google/technology/ai/'
    isWithinSearchWeek = True
    options.page_load_strategy = 'eager'
    driver = webdriver.Chrome(options=options)
    driver.get(pageUrl)
    blogs_list = []

    while (isWithinSearchWeek):
        # Wait until all blogs are presented on the web
        try:
            articles = WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'nav.article-list__feed div.feed-article')))
        except TimeoutException:
            print('Loading take too long')
            break
        # print(articles)
        last_article_date = articles[-1].find_element(By.CSS_SELECTOR, 'time.uni-timesince').get_attribute('datetime')
        last_article_date = datetime.strptime(last_article_date.split(' ')[0], '%Y-%m-%d')

        # Check for the last post's published date, if within the target week, keep loading more contents
        if (datetime.now() - last_article_date) > timedelta(weeks=targetNumWeek):
            for article in articles:
                title = article.find_element(By.CSS_SELECTOR, 'h3.feed-article__title').text
                date = article.find_element(By.CSS_SELECTOR, 'time.uni-timesince').get_attribute('datetime')
                date = datetime.strptime(date.split(' ')[0], '%Y-%m-%d')
                link = article.find_element(By.CSS_SELECTOR, 'div.feed-article > a').get_attribute('href')
                if (datetime.now() - date) > timedelta(weeks=targetNumWeek):
                    isWithinSearchWeek = False
                    break
                blogs_list.append([date.strftime(outputDateFormat), title, link])
            break

        # Load more stories
        load_more_btn = driver.find_element(By.CSS_SELECTOR, 'button.article-list__load-more--cards')
        load_more_btn.send_keys(Keys.ENTER)

    # Write data into file
    writeScrapedData('Google Blog AI', fileName, blogs_list, targetNumWeek)
    print('Scraping Google Blog AI Finished')
    driver.quit()


@handle_scrape_errors
def scrapeDevelopersArchives(targetNumWeek):
    print('Starting scraping Developers Archives...')
    pageUrl = 'https://pages.near.org/blog/category/developers/'
    isWithinSearchWeek = True
    options.page_load_strategy = 'eager'
    driver = webdriver.Chrome(options=options)
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


@handle_scrape_errors
def scrapeAlchemyBlog(targetNumWeek):
    print('Starting scraping Alchemy Blog...')
    pageUrl = 'https://www.alchemy.com/blog'
    isWithinSearchWeek = True
    options.page_load_strategy = 'eager'
    driver = webdriver.Chrome(options=options)
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


@handle_scrape_errors
def scrapeDecrypt(targetNumWeek):
    print('Starting scraping Decrypt...')
    pageUrl = 'https://decrypt.co/news/technology'
    isWithinSearchWeek = True
    options.page_load_strategy = 'eager'
    driver = webdriver.Chrome(options=options)
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


@handle_scrape_errors
def scrapeCointelegraph(targetNumWeek):
    print('Starting scraping Cointelegraph...')
    pageUrl = 'https://cointelegraph.com/'
    isWithinSearchWeek = True
    options.page_load_strategy = 'eager'
    driver = webdriver.Chrome(options=options)
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


@handle_scrape_errors
def scrapeCoinDesk(targetNumWeek):
    print('Starting scraping Coin Desk...')
    pageUrl = 'https://www.coindesk.com/tech/'
    isWithinSearchWeek = True
    options.page_load_strategy = 'eager'
    driver = webdriver.Chrome(options=options)
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


def scrapeZkblab(targetNumWeek):
    print('@zkblab')
    stopSign = 'Nothing here'
    page = 1
    delay = 1.5
    dateFormat = "%d %B %Y"

    pageUrl = 'https://zkplabs.network/blog?page='
    pathLink = "//a[contains(@class,'chakra-link css-spn4bz') and h2]"

    driver = webdriver.Chrome()

    dataList = []
    isEnough = False
    while True:
        driver.get(pageUrl + str(page))
        time.sleep(delay)

        body = driver.find_element(By.TAG_NAME, 'body')
        if (stopSign in body.text):
            print('* Dead end')
            break

        pathLink = "//a[contains(@class,'chakra-link css-spn4bz') and h2]"
        linkList = body.find_elements(By.XPATH, pathLink)

        for link in linkList:
            date = link.find_element(By.TAG_NAME, 'div').text
            title = link.find_element(By.TAG_NAME, 'h2').text
            url = link.get_attribute('href')

            dateTxt = datetime.strftime(datetime.strptime(date, dateFormat), outputDateFormat)
            dataRow = [dateTxt, title, url]

            status = correctTimeOffset(date, dateFormat, targetNumWeek)
            if (not status):
                print('* enough posts')
                isEnough = True
                break

            dataList.append(dataRow)

        if (isEnough):
            break

        print('* still searching')
        page += 1

    # write to file
    with open(fileName, 'a', encoding='UTF8') as file:
        writer = csv.writer(file)

        writer.writerow(['=== FKPLAB ==='])
        for data in dataList:
            writer.writerow(data)
        writer.writerow([])

    print('> done')
    driver.quit()


def scrapeGoogleLab(targetNumWeek):
    print('@google lab')
    delay = 1.5
    url = 'https://blog.google/technology/developers/'
    dateFormat = '%Y-%m-%d'
    isEnough = False

    btnPath = "//button[@class='article-list__load-more--cards js-load-more-button']"
    path2 = "//span[@class='article-list__loader-text']"
    postPath = "//div[@class='feed-article ng-scope']"
    datePath = "//span[@class='eyebrow__date]"

    driver = webdriver.Chrome()
    site = driver.get(url)
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

                dataRow = [date,title,url]

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

        with open(fileName, 'a', encoding='UTF8') as  file:
            writer = csv.writer(file)

            writer.writerow(['=== GoogleLab ==='])
            for data in dataList:
                writer.writerow(data)
            writer.writerow([])

    except Exception as err:
        print(err)

    print('> done')
    driver.quit()


def scrapeApple(targetNumWeek):
    print('@apple')
    pageUrl = 'https://www.apple.com/au/newsroom/archive/?page='
    page = 1
    delay = 1.2
    dateFormat = "%d %B %Y"

    postPath = "//a[@class='result__item row-anchor']"

    driver = webdriver.Chrome()

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

    with open(fileName, 'a', encoding='UTF8') as file:
        writer = csv.writer(file)

        writer.writerow(['=== Apple ==='])
        for data in dataList:
            writer.writerow(data)
        writer.writerow([])

    print('> done')
    driver.quit()


def scrapeForteLab(targetNumWeek):
    print('@fortelab')
    pageUrl = 'https://fortelabs.com/blog/?page='
    page = 1
    delay = 1.2
    dateFormat = "%B %d, %Y"

    postPath = "//h3[@class='elementor-post__title']"

    driver = webdriver.Chrome()

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

    with open(fileName, 'a', encoding='UTF8') as  file:
        writer = csv.writer(file)

        writer.writerow(['=== ForteLab ==='])
        for data in dataList:
            writer.writerow(data)
        writer.writerow([])

    print('> done')
    driver.quit()


def scrapeAliAbdaal(targetNumWeek):
    print('@Ali Abdaal')
    url = "https://aliabdaal.com/articles/page/"
    page = 1
    delay = 1.2
    dateFormat = '%B %d, %Y'
    isEnough = False

    postPath = '//div[@style="box-shadow: rgba(149, 157, 165, 0.2) 0px 8px 24px;"]'

    driver = webdriver.Chrome()

    dataList = []
    while page <= 3:
        driver.get(url + str(page) + '/')
        time.sleep(delay)

        posts = driver.find_elements(By.XPATH, postPath)
        for post in posts:
            postUrl = post.find_element(By.TAG_NAME, 'a').get_attribute('href')
            postTitle = post.find_element(By.TAG_NAME, 'h3').text
            postTime = post.find_elements(By.TAG_NAME, 'h4')[1].text

            timeTxt = datetime.strftime(datetime.strptime(postTime, dateFormat), outputDateFormat)
            dataRow = [timeTxt, postTitle, postUrl]
            # print(dataRow)

            if not correctTimeOffset(postTime, dateFormat, targetNumWeek):
                print('* enough post')
                isEnough = True
                break

            dataList.append(dataRow)

        if isEnough:
            break

        page += 1
        print('* still searching')

    with open(fileName, 'a', encoding='UTF8') as file:
        writer = csv.writer(file)

        writer.writerow(['=== Ali Bdaal ==='])
        for data in dataList:
            writer.writerow(data)
        writer.writerow([])

    print('> done')


def scrapeGfi(targetNumWeek):
    print('@getting gfi blockchain')
    url = 'https://gfiblockchain.com/bai-viet-moi-nhat-tu-gfs.html'
    # numScroll = 5
    delayScroll = 1.2
    dateFormat = "%d/%m/%Y"
    curLen = 0

    driver = webdriver.Chrome()
    driver.get(url)

    body = driver.find_element(By.TAG_NAME, "body")
    while True:
        pathHeader = "//h3[@class='jeg_post_title']"
        headers = driver.find_elements(By.XPATH, pathHeader)

        pathTime = "//div[@class='jeg_meta_date']"
        dates = driver.find_elements(By.XPATH, pathTime)

        if (len(headers) == curLen):
            print('no new posts')
            break

        # finding approriate post
        isEnough = False
        dataList = []
        for i in range(len(headers)):
            publishedTime = datetime.strptime(dates[i].text, dateFormat)
            timeDiff = datetime.now() - publishedTime

            timeRow = publishedTime.strftime(outputDateFormat)
            title = headers[i].text
            urlRow = headers[i].find_element(By.TAG_NAME, 'a').get_attribute('href')

            # print(timeRow, headerRow)

            if (timeDiff > timedelta(weeks=targetNumWeek)):
                print('* enough posts')
                isEnough = True
                break

            dataList.append([timeRow, title, urlRow])

        if (isEnough):
            # start listing
            with open(fileName, 'a', encoding='UTF8') as file:
                writer = csv.writer(file)

                writer.writerow(['=== GFI ==='])
                for data in dataList:
                    writer.writerow(data)
                writer.writerow([])
            break

        body.send_keys(Keys.PAGE_DOWN)
        print('* still searching')
        time.sleep(delayScroll)

    print('> done')
    driver.quit()

def scrapeBankless(targetNumWeek):
    print('@Bankless')
    pageUrl = 'https://www.bankless.com/read'
    dateFormat = "%b %d, %Y"
    page = 1

    driver = webdriver.Chrome()
    driver.get(pageUrl)

    postPath = "//a[@class='item articleBlockSmall']"
    postTitlePath = "h1[class='wow fadeInUp']"
    postDatePath = "div[class='meta wow fadeInUp'] span"

    dataList = []
    isEnough = False
    while True:
        posts = driver.find_elements(By.XPATH, postPath)
        for post in posts:
            postUrl = post.get_attribute('href')

            # open in new tab
            driver.execute_script(f'window.open("{postUrl}","_blank");')
            driver.switch_to.window(driver.window_handles[1])
            time.sleep(3)

            # process post date
            postTitle = driver.find_element(By.CSS_SELECTOR, postTitlePath).text
            postDate = driver.find_elements(By.CSS_SELECTOR, postDatePath)[1].text.split(' ')
            if len(postDate[1]) == 2:
                postDate[1] = '0' + postDate[1]
            postDate = ' '.join(postDate)
            
            # print(dataRow)

            if not correctTimeOffset(postDate, dateFormat, targetNumWeek):
                print("* enough posts")
                isEnough = True
                break

            postDate = datetime.strftime(datetime.strptime(postDate, dateFormat), outputDateFormat)
            dataRow = [postDate, postTitle, postUrl]
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

    with open(fileName, 'a', encoding='UTF8') as file:
        writer = csv.writer(file)

        writer.writerow(['=== Bankless ==='])
        for data in dataList:
            writer.writerow(data)
        writer.writerow([])

    print('> done')
    driver.quit()

def scrapeCoin98(targetNumWeek):
    print('@Coin98')
    pageUrlBase = 'https://coin98.net/posts/title/'
    pageUrlEnds = [
        'buidl'
        ,'research'
        ,'invest'
        ,'he-sinh-thai'
        ,'regulation']
    dateFormat = '%d %b, %Y'

    postPath = 'div.style_cardInsight__F9av_'
    postUrlPath = 'a.style_no-underline__FM_LN'
    postTitlePath = 'div.card-post-title'
    postDatePath = 'div.card-time span'
    driver = webdriver.Chrome()

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
            for data in dataList:
                writer.writerow(data)
            writer.writerow([])

    print('> done')
    driver.quit()

def scrapeVitalik(targetNumWeek):
    print('@Vitalik')
    pageUrl = 'https://vitalik.ca/'
    dateFormat = '%Y %b %d'

    driver = webdriver.Chrome()
    driver.get(pageUrl)

    posts = driver.find_elements(By.TAG_NAME, 'li')
    dataList = []
    for post in posts:
        postDate = post.find_element(By.TAG_NAME, 'span').text
        postTitle = post.find_element(By.TAG_NAME, 'a').text
        postUrl = post.find_element(By.TAG_NAME, 'a').get_attribute('href')

        if not correctTimeOffset(postDate, dateFormat, targetNumWeek):
            print('* enough post')
            break

        postDate = datetime.strftime(datetime.strptime(postDate, dateFormat), outputDateFormat)
        dataRow = [postDate, postTitle, postUrl]
        # print(dataRow)
        dataList.append(dataRow)
    
    with open(fileName, 'a', encoding='UTF8') as file:
        writer = csv.writer(file)

        writer.writerow(['=== vitalik ==='])
        for data in dataList:
            writer.writerow(data)
        writer.writerow([])
    dataList = []


# everything start here
def webscrape(targetNumWeek=1):
    # reset
    with open(fileName, 'w') as file:
        file.flush()

    print(f'scraping weeks: {targetNumWeek}')
    # Academy Binance
    scrapeAcademyBinance(targetNumWeek)

    # Chainlink
    # scrapeChainlink(targetNumWeek)

    # OpenAI
    # scrapeOpenAI(targetNumWeek)

    # Google Blog AI
    # scrapeGoogleBlogAI(targetNumWeek)

    # Developers Archives
    # scrapeDevelopersArchives(targetNumWeek)

    # Alchemy Blog
    # scrapeAlchemyBlog(targetNumWeek)

    # Decrypt
    scrapeDecrypt(targetNumWeek)

    # Cointelegraph
    # scrapeCointelegraph(targetNumWeek)

    # Coin Desk
    # scrapeCoinDesk(targetNumWeek)

    # scrapeZkblab(targetNumWeek)
    # scrapeGoogleLab(targetNumWeek)
    # scrapeApple(targetNumWeek)
    # scrapeForteLab(targetNumWeek)
    # scrapeAliAbdaal(targetNumWeek)
    # scrapeGfi(targetNumWeek)
    # scrapeBankless(targetNumWeek)
    # scrapeCoin98(targetNumWeek)
    # scrapeVitalik(targetNumWeek)
    print('** done')


# virtual desktop to prevent opening sites
display = Xvfb()
display.start()

# start scraping
inputWeek = 5
if (len(sys.argv) > 1):
    inputWeek = int(sys.argv[1])

webscrape(inputWeek)

display.stop()
