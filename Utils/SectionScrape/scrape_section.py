from __future__ import annotations
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
from globals import outputDateFormat


class WebSection:
    
    # Default values
    _explicit_wait = 8
    _as_link = False

    def __init__(self, driver: WebDriver) -> None:
        self._driver = driver


    def useSectionPath(self, path: str, by = By.CSS_SELECTOR, *args, on_error: str = "Section not avaiable") -> WebSection:
        self._section_path = (by, path)
        self._on_section_error = on_error
        return self


    def useTitlePath(self, path: str, by = By.CSS_SELECTOR) -> WebSection:
        self._title_path = (by, path)
        return self


    def useDatePath(self, path: str, by = By.CSS_SELECTOR, in_date_format: str = '', custom_date_format = None) -> WebSection:
        self._date_path = (by, path)
        self._in_date_format = in_date_format
        self._format_date = custom_date_format  # Custom date format function, MUST RETURN datetime to work properly. if not provided, it will use the default date format.
        return self


    def useLinkPath(self, path: str, by = By.CSS_SELECTOR, use_self = False) -> WebSection:
        self._link_path = (by, path)
        self._use_link_self = use_self
        return self


    def as_link(self, use_scraped_as_link: bool) -> WebSection:
        self._as_link = use_scraped_as_link

        return self


    def get_all_data(self) -> list:
        try:
            all_posts = WebDriverWait(self._driver, self._explicit_wait).until(EC.presence_of_all_elements_located(self._section_path))
        except Exception:
            print(self._on_section_error)
            return
        
        if all_posts is None:
            return []

        return all_posts


    def extract_title(self, post) -> str:
        return post.find_element(*self._title_path).get_attribute('textContent').replace('\n', '').strip()


    def extract_date(self, post) -> datetime:
        date = post.find_element(*self._date_path).get_attribute('textContent')
        if self._in_date_format != '':
            date = datetime.strptime(date, self._in_date_format)
        else:
            date = self._format_date(date)
        return date


    def extract_link(self, post) -> str:
        if self._use_link_self:
            return post.get_attribute('href')
        else:
            return post.find_element(*self._link_path).get_attribute('href')


    def extract_data(self, post) -> tuple[datetime, str, str]:
        # Variables initialization
        date: datetime = None
        title: str = None
        link: str = None

        # Extracting
        if self._as_link:
            date, title, link = self.extract_as_link(post)
        else:
            title = self.extract_title(post)
            date = self.extract_date(post)
            link = self.extract_link(post)

        return date, title, link


    def extract_as_link(self, post) -> tuple[datetime, str, str]:
        # Get link
        link = self.extract_link(post)
        
        # Open the link in a new tab and switch to it
        self._driver.execute_script(f'window.open("{link}","_blank");')
        self._driver.switch_to.window(self._driver.window_handles[1])

        # Collect Title and date
        title = self.extract_title(self._driver)
        date = self.extract_date(self._driver)

        # Close the new tab and switch back to the main tab
        self._driver.close()
        self._driver.switch_to.window(self._driver.window_handles[0])

        return date, title, link


    def scrape_in(self, *args, week: int, article_sorted: bool = True) -> tuple[list, bool]:
        """Scrape the section and return the list of articles within the search week

        Args:
            week (int): The number of weeks to search

            article_sorted (bool, optional): Is the article sorted? when sorted, scrape will stop the moment the date
            falls out of search week, otherwise scrape everything. Defaults to True.

            use_scraped_as_link (bool, optional): This is used in case where certain properties cant be found on the main 
            list, which then require to specifically go into each article to check. Be cautious when using this as link path 
            must be found within the articles list while date and title must use the path in the particular article page. Defaults to False.

        Returns:
            tuple[list, bool]: The list of articles and a boolean value indicating if the search week is within the range
        """

        blogs_list = []
        within_search_week = True
        
        all_posts = self.get_all_data()

        for post in all_posts:
            # Collect Title, date and Link
            date, title, link = self.extract_data(post)

            # Check if the post is within the search week
            if (datetime.now() - date) > timedelta(weeks=week):
                if article_sorted:
                    within_search_week = False
                    break
                else: continue
            blogs_list.append([date.strftime(outputDateFormat), title, link])

        return blogs_list, within_search_week


    def scrape_last(self) -> tuple[datetime, str, str]:
        all_posts = self.get_all_data()
        last_post = all_posts[-1]
        return self.extract_data(last_post)
        

# def scrapeFirstSession():
#     try:
#         first_article = driver.find_element(By.CSS_SELECTOR, 'main > div > article > div > div > div:first-child > article > div:last-child')
#     except Exception:
#         print("First article session not avaiable")
#         return

#     # print(first_article.text)
#     title = first_article.find_element(By.CSS_SELECTOR, 'div a.linkbox__overlay').get_attribute('innerText')

#     date = first_article.find_element(By.CSS_SELECTOR, 'div footer > div:first-child time:first-child').text
#     date = datetime.strptime(date, '%b %d, %Y')

#     link = first_article.find_element(By.CSS_SELECTOR, 'div a.linkbox__overlay').get_attribute('href')
#     if (datetime.now() - date) > timedelta(weeks=targetNumWeek):
#         # Return True when enough post so that it can stop the loop
#         return True
#     blogs_list.append([date.strftime(outputDateFormat), title, link])
