from selenium import webdriver
from unittest.mock import patch
from deepaix.common.driver import (
    setup_driver,
    find_latest_chromedriver_version,
    get_chrome_opetions,
)


def test_find_latest_chromedriver_version():
    version = find_latest_chromedriver_version()
    assert isinstance(version, str)


def test_get_chrome_opetions():
    options = get_chrome_opetions()
    assert isinstance(options, webdriver.ChromeOptions)


def test_setup_driver():
    driver = setup_driver()
    assert isinstance(driver, webdriver.Chrome)
