from selenium.common.exceptions import WebDriverException


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


# Open website with retries
def open_with_retries(driver, url, max_retries=10):
    retries_count = 0
    while retries_count < max_retries:
        try:
            driver.get(url)
            return driver
        except WebDriverException:
            print('An error occured while opening the website')
            retries_count += 1
            print(f'Retrying... Attempt {retries_count}')

    print(f'Scrape aborted due to website could not be opened properly after {retries_count} attempts')
    return None
