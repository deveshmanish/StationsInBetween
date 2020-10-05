import codecs
import time

import pandas as pd
import pyautogui
import requests
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

searchurl = 'https://indiarailinfo.com/atlas'
searchBoxID = 'TrkStnListBox'
searchButtonID = 'SearchTrkStn'
# stationDropDownTableClass = 'dropdowntable'
stationDropDownTableClass = 'leaflet-popup-content'
linkText = 'LappGetStationList'
stationDropDownTableXPATH = "//*[contains(text(), 'LappGetStationList')]"
stationInfoClass = 'ltGrayColor primaryColor'

#   Wait for the given element to load
def wait(type, value, driver):
    try:
        element = WebDriverWait(driver, 60).until(          # Time in seconds to be specified here in place of 60
            EC.presence_of_element_located(type, value)
        )
    finally:
        holder = driver.find_element(type, value)
        return holder

#   Formats the code properly before returning it
def decodeText(string):
    return codecs.escape_decode(bytes(string.text, "utf-8"))[0].decode("utf-8")

#   Set various options for the driver such as headless mode, and download directory
def getDriver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.headless = True
    prefs = {
        "download.prompt_for_download": False,
        "directory_upgrade": True,
        '--headless': True}
    options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(options=options)
    driver.create_options()
    return driver

#   Fetch station code for a station by passing the station name as argument
def getStationCode(stationName):
    url = "https://indianrailways.p.rapidapi.com/findstations.php"
    query = {
        "station": stationName
    }
    headers = {
        "x-rapidapi-host": "indianrailways.p.rapidapi.com",
        "x-rapidapi-key": "0450a79c35msh93bb6036bf2aaabp13e5c4jsna13bf65265c4",
        "useQueryString": 'true'
    }
    try:
        r = requests.get(url, params=query, headers=headers)
        r.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)
    if (r.status_code == 200):
        stations = r.json().get('stations')
        for station in stations:
            if stationName.upper() in station['stationName']:
                stationCode = station['stationCode']
                print(stationCode)
                return stationCode
        return 'Please check the station code'

#   Fetch the list of stations between two given station codes, returns a Pandas dataframe
def getData(code):
    heading = ['STATION CODE', 'STATION NAME', 'RAILWAY ZONE', 'RAILWAY DIVISION', 'DISTRICT', 'STATE']
    body = []
    station = {}
    # driver = getDriver()
    driver = webdriver.Chrome()
    driver.get(searchurl)

    # searchBox = driver.find_element(By.ID, searchBoxID)
    searchBox = wait(By.ID,searchBoxID,driver)

    searchBox.send_keys(code)
    searchBox.click()

    # searchBox.send_keys()

    # dropDownTable = driver.find_element(By.PARTIAL_LINK_TEXT,linkText)

    dropDownTable = wait(By.CLASS_NAME,'list hideslow',driver)
    # hidden = driver.find_element(By.XPATH,"//input[@id='']")
    # driver.execute_script("arguments[0].setAttribute('style','visibility:visible;');", hidden)
    driver.execute_script("arguments[0].click();", dropDownTable)
    dropDownTableBody = dropDownTable.find_element(By.TAG_NAME,'tbody')
    for entry in dropDownTableBody.find_elements(By.TAG_NAME,'tr'):
        if entry.get_attribute('rownum')==0 and entry.get_attribute('class')=='rowM1':
            for item in entry.find_elements(By.TAG_NAME,'td'):
                if item.get_attribute('class')=='icol':
                    station.update({
                        'STATION NAME' : decodeText(item)
                    })
                if item.get_attribute('class')=='jcol':
                    list = decodeText(item).split('-')
                    division = list[1][:list[1].find('Div')]
                    station.update({
                        'RAILWAY ZONE' : list[0],
                        'RAILWAY DIVISION' : division
                    })
            print(station)
    searchButton = driver.find_element(By.ID,searchButtonID)
    searchButton.click()

    stationCard = driver.find_element(By.CLASS_NAME,stationInfoClass)

    heading = stationCard.find_element(By.TAG_NAME,'h2').text
    platformString = heading[heading.find('('):heading.find(')')]
    platformList = platformString.split(' ')
    platforms = platformList[0]
    station.update({
        'PLATFORMS': platforms
    })
    infoText = decodeText(stationCard)
    print(infoText)


    # body = filter(None, body)
    # columns = ['Section', 'STATION CODE', 'STATION NAME', 'INTER - DISTANCE']
    # df = pd.DataFrame(body, columns=columns)
    # driver.quit()
    # return df
getData('PU')