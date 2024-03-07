from gc import isenabled
from pickle import FALSE
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from Utils.error_handler import handle_scrape_errors
from Utils.driver_options import create_option
from Utils.write_to_list import writeFileData, writeFileTitle, writeMessage, writeScrapedData
from globals import fileName, outputDateFormat
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from Utils.correct_time_offset import correctTimeOffset
import time
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

# @handle_scrape_errors
def startScrape(targetNumWeek):
  siteTitle = 'Snipd'
  print('--> ' + siteTitle)
  writeFileTitle(siteTitle)
  
  url = 'https://share.snipd.com/show/'
  endpoints = [
    '95d8149f-be0f-41e1-a1be-be27e8657404',
    '51627639-7d0e-4072-a135-cd70891507aa',
    '7cde4a6b-2ddc-4322-9012-f4a6b9150836',
    '702d02d9-da00-45fc-a1cf-eec98a7b77b8',
    '7ed81b6d-3a41-44f8-8cef-346292b9ead0',
    '8da2bdcc-bdd8-44f6-9897-8b521741cad9',
    'd81f0385-a5f4-4667-ad8c-2c59848b2f21',
    '51fb9a44-50ca-46b1-a264-c3476840f386',
    'bb0fd336-a7e9-4292-a4fa-b1a97d0193bd',
    'a5fb096e-1a1d-4f17-b3e2-4d19f8019a6b',
    'aeed41f5-58d6-451f-a6fb-27580fc32d82',
    '743fa02c-9056-4fb6-bfde-2980aab7d42a',
    '64770736-8553-415f-be68-ed6627aa04df',
    'd8583c67-6d33-4382-ae76-624bef569aa3',
    '674adf6e-214f-4c22-ad07-b0c318e4ca21',
    '1febacde-cb5a-4f9c-898d-36317d84430d',
    'a8a6f3af-b6eb-44ea-838f-d6e4830dc2e6',
    '64bb0089-b816-4c06-9c77-3f37d97773aa',
    '40822f76-afb9-4a73-897e-a0564ff284b0',
    '12f021e2-d751-4850-9e52-551255bb44dd',
    '95d8149f-be0f-41e1-a1be-be27e8657404',
  ]
  delay = 2
  dateFormat = '%b %d, %Y'
  isEnough = False
  
  postPath = 'a[class="show-episode"]'
  postTitlePath = 'h3'
  postDatePath = 'div[class="episode-subtitle"]'
  
  service = Service(ChromeDriverManager().install())
  options = create_option(headless=True)
  driver = webdriver.Chrome(options=options, service=service)
  
  for endpoint in endpoints:
    print(f'> {url + endpoint}')
    writeMessage(fileName, f'> {url + endpoint}')
    curPg = 0
    isEnough = False
    dataList = []
    
    while True:
      urlAll = url + endpoint + '?page=' + str(curPg)
      driver.get(urlAll)
      time.sleep(delay)
      
      for post in driver.find_elements(By.CSS_SELECTOR, postPath):
        postTitle = post.find_element(By.TAG_NAME, postTitlePath).text
        postUrl = post.get_attribute('href')
        postDate = post.find_element(By.CSS_SELECTOR, postDatePath).text.split(' • ')[0]
        
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
        
      if isEnough:
        print('> done\n')
        writeFileData(dataList, targetNumWeek)
        # writeScrapedData(siteTitle + ':' + endpoint, fileName, dataList, targetNumWeek)
        break
      curPg += 1
      print('+ still searching')
      
  driver.quit()
