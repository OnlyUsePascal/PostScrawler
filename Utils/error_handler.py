from selenium.common.exceptions import WebDriverException
from Utils.write_to_list import writeError, log
from globals import logPath, LogFileName
from datetime import datetime
from os.path import join
import traceback

def generate_global_log_filename():
    # Check if there is already a log file
    if LogFileName().get_file() != None:
        return LogFileName().get_file()
    
    # Get the current date and time
    now = datetime.now()

    # Format the date and time as a string
    filename = now.strftime("scraper_log_%Y%m%d_%H%M%S.log")
    
    LogFileName().set_file(filename)

    return filename


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

            log(f'{func.__name__} ran successfully.', join(logPath, generate_global_log_filename()))
        except Exception as e:
            print(f'An error occured')
            print(f'{func.__name__} aborted')

            writeError(f'An error occured at {func.__name__}, please check the logs at '' for more details')
            log(f'An error occured at {func.__name__}:\n{traceback.format_exc()}', join(logPath, generate_global_log_filename()))
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
