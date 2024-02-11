from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from Utils.error_handler import handle_scrape_errors
from Utils.driver_options import create_option
from Utils.write_to_list import writeScrapedData
from globals import fileName, outputDateFormat
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from Utils.correct_time_offset import correctTimeOffset
import time
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

@handle_scrape_errors
def startScrape(targetNumWeek):
  siteTitle = 'BlockWork'
  print('--> ' + siteTitle)
  
  url = 'https://blockworks.co/news'
  print(f'> {url}')
  delay = 2
  dateFormat = '%B %d, %Y'
  isEnough = False
  
  postPath = 'div[class="grid grid-cols-1 grid-rows-[168px_minmax(168px,_1fr)] h-full"]'
  postTitlePath = 'a[class="font-headline flex-grow text-[18px] lg:text-[24px] font-semibold leading-snug hover:text-primary"]'
  postUrlPath = 'a'
  postDatePath = 'time'
  closeBtnPath = 'div[class="sidebar-iframe-close"]'
  
  service = Service(ChromeDriverManager().install())
  options = create_option(headless=True)
  driver = webdriver.Chrome(options=options, service=service)
  
  for _ in range(5):
    driver.get(url)
    isAdClosed = False
    
    try:
      while True: 
        if (not isAdClosed):
          try: 
            WebDriverWait(driver, delay).until(EC.element_to_be_clickable((By.CSS_SELECTOR, closeBtnPath))).click()
            time.sleep(2)
            print('ad close btn found :)')
            isAdClosed = True
          except Exception as err: 
            print('ad close btn not found')
            # print(err)
        else:
          time.sleep(delay)
          
        dataList = []
        posts = driver.find_elements(By.CSS_SELECTOR, postPath)
        for post in posts:
          postTitle = post.find_element(By.CSS_SELECTOR, postTitlePath).text
          postUrl = post.find_element(By.TAG_NAME, postUrlPath).get_attribute('href')
          postDate = post.find_element(By.CSS_SELECTOR, postDatePath).text
          
          try:
            postDate = postDate.split(' ')
            if len(postDate[1]) == 2:
              postDate[1] = '0' + postDate[1]
            postDate = ' '.join(postDate)
            
            if not correctTimeOffset(postDate, dateFormat, targetNumWeek):
              print('* enough post')
              isEnough = True
              break
            
            postDate = datetime.strftime(datetime.strptime(postDate, dateFormat), outputDateFormat)
          except Exception as err:
            # writeScrapedData(siteTitle, fileName, dataList, targetNumWeek, url)
            print('+ some err happened')
            raise err  
          
          dataRow = [postDate, postTitle, postUrl]
          dataList.append(dataRow)
          # print(dataRow)
        
        if (isEnough):
          writeScrapedData(siteTitle, fileName, dataList, targetNumWeek, url)
          print('> done\n')
          driver.quit()
          return
        print('* still searching')
        driver.execute_script("window.scrollTo(0, document.body.clientHeight-100);")
        time.sleep(delay)    
    except Exception as err: 
      print(err)
      print('Reconnecting...\n')
  print('> Connection Failed\n')