from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from datetime import datetime, timedelta
import time
import csv

fileName = 'test.csv'
outputDateFormat = '%Y-%m-%d'

# Selenium driver options
options = Options()
options.add_argument('--headless')  # No window opened
options.add_experimental_option("excludeSwitches", ["enable-logging"])  # Disable logging
# options.add_argument("--log-level=3")
options.page_load_strategy = 'eager'

# Write data function


def writeScrapedData(data_title: str, file, data_list: list, target_weeks):
    with open(file, 'a', encoding="utf-8") as file:
        writer = csv.writer(file)

        writer.writerow([f'=== {data_title} ==='])
        if not data_list:
            writer.writerow([f'No articles/blogs were found within {target_weeks} weeks'])
            return
        for data in data_list:
            writer.writerow(data)

# Ultilities funtion
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
            title = blog.find_element(By.CSS_SELECTOR, 'p > a').text
            date = datetime.strptime(blog.find_element(By.CSS_SELECTOR, 'div:first-child > div:nth-child(2)').text, '%B %d, %Y')
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
            for article in articles:
                title = article.find_element(By.CSS_SELECTOR, 'div:last-child article h3 span').text
                date = datetime.strptime(article.find_element(By.CSS_SELECTOR, 'div:first-child > h4').text, '%b %d, %Y')
                link = article.find_element(By.CSS_SELECTOR, 'div:last-child article h3 a').get_attribute('href')
                if (datetime.now() - date) > timedelta(weeks=targetNumWeek):
                    isWithinSearchWeek = False
                    break
                blogs_list.append([date.strftime(outputDateFormat), title, link])
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
            articles = WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'ul.posts-listing__list > li.posts-listing__item')))
        except TimeoutException:
            print('Loading take too long')
            break
        # Get last post's date
        last_article_date = articles[-1].find_element(By.CSS_SELECTOR, 'div time').text
        try:
            last_article_date = datetime.strptime(last_article_date, '%b %d, %Y')
        except Exception:
            last_article_date = datetime.now()
        # print(last_article_date)

        # Check for the last post's published date, if within the target week, keep loading more contents
        if (datetime.now() - last_article_date) > timedelta(weeks=targetNumWeek):
            for article in articles:
                # skip if target has this class
                if 'posts-listing__item_triple' in article.get_attribute('class').split():
                    continue

                # Some posts are empty, this is to prevent it
                try:
                    title = article.find_element(By.CSS_SELECTOR, 'header.post-card__header span.post-card__title').text
                    link = article.find_element(By.CSS_SELECTOR, 'header.post-card__header > a.post-card__title-link').get_attribute('href')
                except Exception:
                    continue
                # Get date, return today if it was posted n times ago
                try:
                    date = datetime.strptime(article.find_element(By.CSS_SELECTOR, 'div time').text, '%b %d, %Y')
                except Exception:
                    date = datetime.now()

                if (datetime.now() - date) > timedelta(weeks=targetNumWeek):
                    isWithinSearchWeek = False
                    break
                blogs_list.append([date.strftime(outputDateFormat), title, link])
            break

        # Scroll down to bottom to load more articles
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight - 100);")
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
    print('getting zkblab')
    # targetNumWeek = 2
    pageUrl = 'https://zkplabs.network/blog?page='
    stopSign = 'Nothing here'
    page = 1
    delay = 1.5
    dateFormat = "%d %B %Y"

    driver = webdriver.Chrome()

    dataList = []
    isEnough = False
    while (page <= 6):
        driver.get(pageUrl + str(page))
        time.sleep(delay)

        body = driver.find_element(By.TAG_NAME, 'body')
        if (stopSign in body.text):
            print('* Dead end')
            break

        pathLink = "//a[contains(@class,'chakra-link css-spn4bz') and h2]"
        linkList = body.find_elements(By.XPATH, pathLink)

        for link in linkList:
            publishedTime = datetime.strptime(link.find_element(By.TAG_NAME, 'div').text, dateFormat)
            title = link.find_element(By.TAG_NAME, 'h2').text
            url = link.get_attribute('href')

            # print(publishedTime.strftime(outputDateFormat))
            # print(datetime.now() - publishedTime)
            # print(title)
            # print(url)
            # print('====')

            timeDiff = datetime.now() - publishedTime
            if (timeDiff > timedelta(weeks=targetNumWeek)):
                print('* enough posts')
                isEnough = True
                break

            dataList.append([publishedTime.strftime(outputDateFormat), title, url])

        if (isEnough):
            break
        page += 1

    # write to file
    with open(fileName, 'a', encoding='UTF8') as file:
        writer = csv.writer(file)

        writer.writerow(['=== FKPLAB ==='])
        for data in dataList:
            writer.writerow(data)

    print('> done')
    driver.quit()


def scrapeGfi(targetNumWeek):
    print('getting gfi blockchain')
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
                print('enough posts')
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
            break

        body.send_keys(Keys.PAGE_DOWN)
        print('scrolled =====')
        time.sleep(delayScroll)

    print('> done')
    driver.quit()


# everything start here
def webscrape(targetNumWeek=1):
    # reset
    with open(fileName, 'w') as file:
        file.flush()

    # Academy Binance
    # scrapeAcademyBinance(targetNumWeek)

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
    # scrapeDecrypt(targetNumWeek)

    # Cointelegraph
    # scrapeCointelegraph(targetNumWeek)

    # Coin Desk
    # scrapeCoinDesk(targetNumWeek)

    # zkplab
    # scrapeZkblab(targetNumWeek)

    # gfi
    # scrapeGfi(targetNumWeek)


webscrape(3)
