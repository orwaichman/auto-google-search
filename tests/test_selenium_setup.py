import os
import pytest
from selenium import webdriver
from selenium.common.exceptions import WebDriverException

from const import WEBDRIVER_PATH


@pytest.mark.dependency()
def test_webdriver():
    if not os.path.exists(WEBDRIVER_PATH):
        raise WebDriverException(
            "Webdriver configured path was found. Make sure GeckoDriver is installed and path is correct in const.py")


@pytest.mark.dependency(depends=['test_webdriver'])
def test_firefox():
    try:
        driver = webdriver.Firefox(executable_path=WEBDRIVER_PATH)
        driver.quit()
    except WebDriverException:
        raise WebDriverException("It seems like Firefox is not installed.")
