from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
from datetime import date
import mysql.connector


#functions for scraping tcgplayer, specificly one piece cards
def get_name(i,driver):
    try:
        name = driver.find_element(By.XPATH,f"/html/body/div[2]/div/div/section[2]/section/section/section/section/section/div[{str(i)}]/div/div/div/div/a/section/span").text
    except Exception as e:
        name = "NA"
        driver.quit()
        print(f"Error fetching name: {e}")
    return name

def get_rarity(i,driver):
    try:
        rarity = driver.find_element(By.XPATH,f"/html/body/div[2]/div/div/section[2]/section/section/section/section/section/div[{str(i)}]/div/div/div/div/a/section/section[2]/div/span[1]").text[:-1]
    except:
        rarity = "NA"
    return rarity

def get_card_num(i,driver):
    try:
        card_num = driver.find_element(By.XPATH,f"/html/body/div[2]/div/div/section[2]/section/section/section/section/section/div[{str(i)}]/div/div/div/div/a/section/section[2]/div/span[2]").text[1:]
    except:
        card_num = "NA"
    return card_num

def get_url(i,driver):
    try:
        url = driver.find_element(By.XPATH,f"/html/body/div[2]/div/div/section[2]/section/section/section/section/section/div[{str(i)}]/div/div/div/div/a").get_attribute('href')
    except:
        url = "NA"
    return url

def get_card_set(i,driver):
    try:
        card_set = driver.find_element(By.XPATH,f"/html/body/div[2]/div/div/section[2]/section/section/section/section/section/div[{str(i)}]/div/div/div/div/a/section/h4/div").text
    except:
        card_set = "NA"
    return card_set

def get_market_price(i,driver):
    try:
        market_price = float(driver.find_element(By.XPATH,f"/html/body/div[2]/div/div/section[2]/section/section/section/section/section/div[{str(i)}]/div/div/div/div/a/section/section[3]/section/span[2]").text[1:].replace(",", ""))
    except:
        market_price = 0
    return market_price

#scraping all one piece cards into csv

def scrape_tcgplayer():

    chromedriver_path = "/usr/bin/chromedriver"

    chrome_options = Options()
    chrome_options.add_argument("--headless")  
    chrome_options.add_argument("--no-sandbox")  
    chrome_options.add_argument("--disable-dev-shm-usage")  

    service = Service(chromedriver_path)

    driver = webdriver.Chrome(service=service, options=chrome_options)




    #url to scrape
    url = "https://www.tcgplayer.com/search/one-piece-card-game/product?productLineName=one-piece-card-game&page=1&view=grid"
    
    driver.get(f"{url}")
    main = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, "search-result"))
            )
    
    next_page_XPATH = "/html/body/div[2]/div/div/section[2]/section/section/section/section/div[2]/a[2]"


    
    WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, next_page_XPATH))
            )

    #while loop to scrape each page until it breaks at last page
    try:
        q = False
        while q == False:
            WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.XPATH, next_page_XPATH))
                )
            for i in range(1,len(driver.find_elements(By.CLASS_NAME, "search-result")) + 1):
                url = get_url(i,driver)
                name = get_name(i,driver)
                card_num = get_card_num(i,driver)
                rarity = get_rarity(i,driver)
                card_set = get_card_set(i,driver)
                market_price = get_market_price(i,driver)
                val = (name,card_num,rarity,market_price,card_set,url,date_today)
                print([name,card_num,rarity,market_price,card_set])
                mycursor.execute(sql,val)
            try:
                link = driver.find_element(By.XPATH, next_page_XPATH).get_attribute("href")
                driver.get(link)
            except:
                print("at max page")
                q = True
                break
                
    except Exception as e:
        driver.quit()
        print(f"Error: {e}")
        send_report(f'{e}')
    
    time.sleep(5)
    driver.quit()

#database connection
mydb = mysql.connector.connect(
    host = 'localhost',
    user = 'root',
    passwd = 'somepasswd',
    database = 'somedb'
    )

mycursor = mydb.cursor()
sql = 'INSERT INTO table(name,card_num,rarity,market_price,card_set,url,date) values (%s,%s,%s,%s,%s,%s,%s)'
date_today = str(date.today())


start_time = time.time()
scrape_tcgplayer()
end_time = time.time()

elapsed_time = end_time - start_time
print(f"Code finished in {elapsed_time} seconds")
mydb.commit()

mycursor.close()
mydb.close()
