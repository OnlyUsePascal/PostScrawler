from selenium.webdriver.chrome.options import Options


def create_option(headless: bool = True, page_load_strategy: str = 'eager') -> Options:
    """Create a common driver option for scraping website, default option are always headless
    and eager page load strategy

    Args:
        headless (bool, optional): Whether to make the web browser window open or stay hidden. Defaults to True.
        page_load_strategy (str, optional): The way selenium load website, prefer more to the documentation. Defaults to 'eager'.

    Returns:
        Options:
    """
    # Selenium driver options
    options = Options()

    if headless:
        options.add_argument('--headless=new')  # No window opened
    options.add_experimental_option("excludeSwitches", ["enable-logging"])  # Disable logging
    options.add_argument("--log-level=3")  # Disable logging
    options.page_load_strategy = page_load_strategy
    return options
