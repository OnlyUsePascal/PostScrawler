from gc import isenabled
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
  siteTitle = 'Okx'
  print('--> ' + siteTitle)
  
  url = 'https://www.okx.com/learn/tag/'
  endpoints = [
    'security',
    'metaverse',
    'nft',
    'bitcoin',
    'gamefi',
    'altcoin',
    'research',
    'blockchain',
    'web3',
    'layer2',
  ]
  delay = 3
  dateFormat = '%b %d, %Y'
  isEnough = True
  
  postNumPath = 'h1[class="index_title__cxXos"]'
  postPath = 'a[class="index_linkWrapper__2A+Kb"]'
  postTitlePath = 'div[class="index_title__0XdIR"]'
  postDatePath = 'div[class="index_date__IHysu"]'
  
  service = Service(ChromeDriverManager().install())
  options = create_option(headless=True)
  driver = webdriver.Chrome(options=options, service=service)
  
  for endpoint in endpoints:
    curPg = 1
    lastPg = 100
    isEnough = False
    dataList = []
    
    while True:
      urlAll = url + endpoint + '/page/' + str(curPg)
      print(urlAll)
      driver.get(urlAll)
      time.sleep(delay)
      
      postNum = driver.find_element(By.CSS_SELECTOR, postNumPath).text.split(' ')[1][1:-1]
      lastPg = int(max(1, int(postNum) / 24))
      # print('last page = ' + str(lastPg))
      
      for post in driver.find_elements(By.CSS_SELECTOR, postPath):
        postTitle = post.find_element(By.CSS_SELECTOR, postTitlePath).text
        postUrl = post.get_attribute('href')
        postDate = post.find_element(By.CSS_SELECTOR, postDatePath).text
        
        postDate = postDate.split(' ')
        if len(postDate[1]) == 2:
          postDate[1] = '0' + postDate[1]
        postDate = ' '.join(postDate)
        
        if not correctTimeOffset(postDate, dateFormat, targetNumWeek):
          isEnough = True
          break
      
        postDate = datetime.strftime(datetime.strptime(postDate, dateFormat), outputDateFormat)
        dataRow = [postDate, postTitle, postUrl]
        dataList.append(dataRow)
        # print(dataRow)
        
      if isEnough or curPg >= lastPg:
        print('> done\n')
        writeScrapedData(siteTitle + ':' + endpoint, fileName, dataList, targetNumWeek)
        break
      curPg += 1
      print('still searching')
      
  driver.quit




