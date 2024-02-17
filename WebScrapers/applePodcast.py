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
from Utils.write_to_list import writeFileData, writeFileTitle, writeMessage, writeScrapedData
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

@handle_scrape_errors
def startScrape(targetNumWeek):
  siteTitle = 'Apple Podcast'
  print('--> ' + siteTitle)
  
  url = 'https://podcasts.apple.com/vn/podcast/'
  endpoints = [
    'blockchain-wont-save-the-world/id1502561115',
    '0xresearch/id1651683074',
    'bankless/id1499409058',
    'bell-curve/id1641356619',
    'blockchain-insider-podcast-by-11-fs/id1256418941',
    'blockdrops-com-maur%C3%ADcio-magaldi/id1491231344',
    'empire/id1554930038',
    'gm-from-decrypt/id1520762610',
    'lightspeed/id1697548240',
    'the-breakdown/id1438693620',
    'the-pomp-podcast/id1434060078',
    'the-scoop/id1460134454',
    'unchained/id1123922160',
    'w3b-talks/id1657782594',
    'whats-on-tap/id1565772450',
    'the-bad-crypto-podcast/id1261133600',
    'bloomberg-crypto/id1623197303',
    'the-money-movement-with-jeremy-allaire-leaders/id1512272543',
    'zero-knowledge/id1326503043'
  ]
  delay = 2
  dateFormat = '%d %b %Y'
  isEnough = True
  
  postPath = 'div[class="l-column  small-valign-top tracks__track__content"]'
  postTitlePath = 'a'
  postDatePath = 'time'
  btnPath = 'button[class="link"]'
  
  service = Service(ChromeDriverManager().install())
  options = create_option(headless=True)
  driver = webdriver.Chrome(options=options, service=service)
  
  writeFileTitle(siteTitle)
  for endpoint in endpoints:
    urlAll = url + endpoint
    print(f'> {urlAll}')
    writeMessage(fileName, f'> {urlAll}')
    driver.get(urlAll)
    time.sleep(delay)
    isEnough = False
    
    while True:
      dataList = []
      for post in driver.find_elements(By.CSS_SELECTOR, postPath):
        postTitle = post.find_element(By.TAG_NAME, postTitlePath).text
        postUrl = post.find_element(By.TAG_NAME, postTitlePath).get_attribute('href')
        postDate = post.find_element(By.TAG_NAME, postDatePath).text
        
        postDate = postDate.split(' ')
        if len(postDate[0]) == 1:
          postDate[0] = '0' + postDate[0]
        if len(postDate[1]) != 3:
          postDate[1] = postDate[1][:-1]
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
        writeFileData(dataList, targetNumWeek)
        break
      
      print('+ still searching')
      try:
        driver.execute_script("window.scrollTo(0, document.body.clientHeight-100);")
        # WebDriverWait(driver, 1).until(EC.element_to_be_clickable((By.CSS_SELECTOR, btnPath))).click()
        driver.execute_script("arguments[0].click();", driver.find_element(By.CSS_SELECTOR, btnPath))
        time.sleep(delay)
      except Exception as err:
        # writeScrapedData(siteTitle + ':' + endpoint, fileName, dataList, targetNumWeek)
        writeFileData(dataList, targetNumWeek)
        print('some err happends?')
        # print(err)
        break
    