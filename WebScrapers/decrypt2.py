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
  siteTitle = 'Decrypt 2: Explainers'
  print('--> ' + siteTitle)
  
  url = 'https://decrypt.co/university/explainers'
  print(f'> {url}')
  delay = 2
  dateFormat = '%b %d, %Y'
  
  postPath = 'div[class="sc-4d03eefa-1 GwgAQ border-neutral-500 border-r-[1px] border-b-[1px]"]'
  postUrlPath = 'a[class="block linkbox__overlay"]'
  postDatePath = 'time'
  loadBtnPath = 'button[class="px-4 text-white border-x-0 border-y-0 bg-gradient-to-r from-course-gradient-from to-course-gradient-to degen-alley-dark:bg-degen-alley-primary degen-alley-dark:bg-none degen-alley-dark:text-black py-2.5 px-4 gap-x-1.5 font-akzidenz-grotesk font-medium text-sm leading-5 rounded-md active:ring-primary-500 inline-flex items-center justify-center border border-solid font-akzidenz-grotesk font-medium whitespace-nowrap active:ring-2 active:ring-offset-1"]'
  closeBtnPath = 'svg[class="svg-inline--fa fa-times fa-w-10 sc-4604b65e-0 lbrsqG"]'
  
  service = Service(ChromeDriverManager().install())
  options = create_option(headless=True)
  driver = webdriver.Chrome(options=options, service=service)

  driver.get(url)
  time.sleep(delay)
  isEnough = False
  isAdClosed = False
  
  dataList = []
  while True: 
    posts = driver.find_elements(By.CSS_SELECTOR, postPath)[-12:]
    # print(posts)
    for post in posts:
      if (not isAdClosed):
        try: 
          WebDriverWait(driver, 1).until(EC.element_to_be_clickable((By.CSS_SELECTOR, closeBtnPath))).click()
          time.sleep(1)
          isAdClosed = True
          print('ad close btn found :)')
        except Exception as err: 
          print('ad close button not found')
          
      postUrl = post.find_element(By.CSS_SELECTOR, postUrlPath).get_attribute('href')
      postTitle = post.find_element(By.CSS_SELECTOR, postUrlPath).text
      postDate = 'null?'
      
      driver.execute_script(f'window.open("{postUrl}","_blank");')
      driver.switch_to.window(driver.window_handles[1])
      postDate = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.TAG_NAME, postDatePath))).text
      driver.close()
      driver.switch_to.window(driver.window_handles[0])
      
      postDate = postDate.split(' ')
      if len(postDate[1]) == 2:
        postDate[1] = '0' + postDate[1]
      postDate = ' '.join(postDate)
      
      if not correctTimeOffset(postDate, dateFormat, targetNumWeek):
        print('+ enough post')
        isEnough = True
        break
      
      postDate = datetime.strftime(datetime.strptime(postDate, dateFormat), outputDateFormat)
      dataRow = [postDate, postTitle, postUrl]
      dataList.append(dataRow)
      # print(dataRow)
    
    if (isEnough):
      writeScrapedData(siteTitle, fileName, dataList, targetNumWeek, url)
      print('> done\n')
      driver.quit()
      break
    
    print('+ still searching')
    try:
      driver.execute_script("window.scrollTo(0, document.body.clientHeight-1500);")
      driver.find_element(By.CSS_SELECTOR, loadBtnPath).send_keys(Keys.ENTER)
      # driver.execute_script("arguments[0].click();", driver.find_element(By.CSS_SELECTOR, loadBtnPath))
      # WebDriverWait(driver, delay).until(EC.element_to_be_clickable((By.CSS_SELECTOR, loadBtnPath))).click()
      time.sleep(2)
    except Exception as err:
      writeScrapedData(siteTitle, fileName, dataList, targetNumWeek, url)
      print(err)
      break
