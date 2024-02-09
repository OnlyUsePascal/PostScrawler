from operator import truediv
from xml.dom.pulldom import PROCESSING_INSTRUCTION
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
from seleniumbase import SB


@handle_scrape_errors
def startScrape(targetNumWeek):
  siteTitle = 'Coinbase:blog/landing'
  print('--> ' + siteTitle)
  
  url = 'https://www.coinbase.com/blog/landing'
  delay = 3
  dateFormat = '%B %d, %Y'
  isEnough = False
  
  postPath = 'div[class="cds-flex-f1g67tkn sc-fe93bc11-0 sc-3dcf3304-0 bWeVQP iWfdgn"]'
  postTitlePath = 'h3'
  postUrlPath = 'a'
  postDatePath = 'p[class="sc-eb4cf3b1-0 eZVAiH"]'
  loadBtnPath = 'button[class="cds-interactable-i9xooc6 cds-transparentChildren-tnzgr0o cds-focusRing-fd371rq cds-transparent-tlx9nbb cds-button-b18qe5go cds-scaledDownState-sxr2bd6 cds-primaryForeground-pxcz3o7 cds-button-bpih6bv cds-4-_1arbnhr cds-4-_hd2z08"]'
  loadIconPath = 'div[class="cds-flex-f1g67tkn sc-fe93bc11-0 fCVndJ"]'
  
  service = Service(ChromeDriverManager().install())
  options = create_option(headless=False)
  driver = webdriver.Chrome(options=options, service=service)
  driver.get(url)
  driver.minimize_window()
  time.sleep(delay)
    
  print('done')
  # return
  while True:
    dataList = []
    
    for post in driver.find_elements(By.CSS_SELECTOR, postPath):
      postTitle = post.find_element(By.TAG_NAME, postTitlePath).text
      postUrl = post.find_element(By.TAG_NAME, postUrlPath).get_attribute('href')
      postDate = post.find_element(By.CSS_SELECTOR, postDatePath).text
      
      postDate = postDate.split(' ')
      if len(postDate[1]) == 2:
        postDate[1] = '0' + postDate[1]
      if (postDate[2][-1] == ','):
        postDate[2] = postDate[2][:-1]
      postDate = ' '.join(postDate)
      
      if not correctTimeOffset(postDate, dateFormat, targetNumWeek):
        isEnough = True
        break
      
      postDate = datetime.strftime(datetime.strptime(postDate, dateFormat), outputDateFormat)  
      dataRow = [postDate, postTitle, postUrl]
      dataList.append(dataRow)
      # print(dataRow)
    
    if isEnough:
      print('> done\n')
      writeScrapedData(siteTitle, fileName, dataList, targetNumWeek)
      break
    
    print('> still searching\n')
    try:
      driver.execute_script("window.scrollTo(0, document.body.clientHeight-1500);")
      driver.find_element(By.CSS_SELECTOR, loadBtnPath).send_keys(Keys.ENTER)
      # driver.execute_script("arguments[0].click();", driver.find_element(By.CSS_SELECTOR, loadBtnPath))
      # WebDriverWait(driver, delay).until(EC.element_to_be_clickable((By.CSS_SELECTOR, loadBtnPath))).click()
      time.sleep(3)
      # WebDriverWait(driver, delay).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, loadIconPath)))
    except Exception as err:
      writeScrapedData(siteTitle, fileName, dataList, targetNumWeek)
      print(err)
      break
    