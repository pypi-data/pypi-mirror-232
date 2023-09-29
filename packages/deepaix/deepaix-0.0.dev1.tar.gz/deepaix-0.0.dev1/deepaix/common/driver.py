from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import requests
from webdriver_manager.chrome import ChromeDriverManager

import subprocess


def find_latest_chromedriver_version():
    url = "https://chromedriver.storage.googleapis.com/LATEST_RELEASE"
    response = requests.get(url)
    version = response.text
    return version


def get_chrome_opetions(download_path: str = None):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--window-size=1920,1200")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    if download_path != None:
        prefs = {"download.default_directory": download_path}
        chrome_options.add_experimental_option("prefs", prefs)

    return chrome_options


def setup_driver(download_path: str = None):
    chrome_options = get_chrome_opetions(download_path)

    try:
        driver_path = ChromeDriverManager().install()
        service = Service(executable_path=driver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
    except Exception as e:
        print(f"ERROR: installing the latest chromedriver")
        latest_version = find_latest_chromedriver_version()
        driver_path = ChromeDriverManager(version=latest_version).install()
        service = Service(executable_path=driver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)

    return driver


def wait_driver_until_all_li_inside_ul(driver, class_name: str):
    wait = WebDriverWait(driver, 10)
    elements = wait.until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, class_name))
    )
    driver.implicitly_wait(10)

    elements[0].find_elements(by=By.CSS_SELECTOR, value="li")
    return driver


def wait_driver_until_element_by_class_name(driver, class_name: str):
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, class_name)))
    driver.implicitly_wait(10)
    return driver


def wait_driver_until_element_by_name(driver, name: str):
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_all_elements_located((By.NAME, name)))
    driver.implicitly_wait(10)
    return driver


def wait_driver_until_element_by_id(driver, id: str):
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_all_elements_located((By.ID, id)))
    driver.implicitly_wait(10)
    return driver
