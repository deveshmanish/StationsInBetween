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

searchurl = 'http://rbs.indianrail.gov.in/ShortPath/ShortPath.jsp'
sourceTextBoxXPATH = '/html/body/div/div[1]/table/tbody/tr[1]/td[1]/center/form/table/tbody/tr[2]/th[1]/input'
destinationTextBoxXPATH = '/html/body/div/div[1]/table/tbody/tr[1]/td[1]/center/form/table/tbody/tr[3]/td[2]/input'
sourceStationID = 'srcCode'
destinationStationID = 'destCode'
routeRadioButtonXPATH = '/html/body/div/div[1]/table/tbody/tr[1]/td[1]/center/form/table/tbody/tr[6]/td[2]/input[3]'
routeRadioButtonID = 'distance'
routeRadioButtonValue = 'engg'
searchButtonID = 'findPath0'
searchButtonXPATH = '/html/body/div/div[1]/table/tbody/tr[1]/td[1]/center/form/table/tbody/tr[3]/td[3]/input'
tableID = 'routetbl'

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
def getData(source, destination):
    heading = ['STATION CODE', 'STATION NAME', 'CUMULATIVE DISTANCE', 'INTER - DISTANCE', 'GAUGE TYPE']
    body = []

    # driver = getDriver()
    driver = webdriver.Chrome()
    driver.get(searchurl)

    sourceTextBox = driver.find_element(By.XPATH, sourceTextBoxXPATH)
    sourceTextBox.send_keys(source)

    destinationTextBox = driver.find_element(By.XPATH, destinationTextBoxXPATH)
    destinationTextBox.send_keys(destination)

    routeButton = driver.find_element(By.XPATH, routeRadioButtonXPATH)
    routeButton.click()

    searchButton = driver.find_element(By.XPATH, searchButtonXPATH)
    searchButton.click()
    result = None
    string = 'plus'
    i = 0
    while result is None:
        text = string + str(i)
        print(text)
        try:
            link = driver.find_element(By.ID, text)
            ActionChains(driver).move_to_element(link).click(link).perform()
            time.sleep(0.1)
            pyautogui.press('esc')
            i = i + 1
        except:
            break

    for tableRow in driver.find_elements(By.ID, tableID):
        bodys = {}
        tableDesc = tableRow.find_element(By.TAG_NAME, 'tbody')
        for rows in tableDesc.find_elements(By.TAG_NAME, 'tr'):
            row = rows.find_elements(By.TAG_NAME, 'td')
            for item in range(len(row)):
                if item == 0:
                    continue
                else:
                    try:
                        bodys.update({
                            heading[item - 1]: decodeText(row[item])
                        })
                    except:
                        continue
            bodys.update({
                'Section': "{}-{}".format(source, destination)
            })
            body.append(bodys.copy())
    body = filter(None, body)
    columns = ['Section', 'STATION CODE', 'STATION NAME', 'INTER - DISTANCE']
    df = pd.DataFrame(body, columns=columns)
    driver.quit()
    return df
