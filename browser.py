import contextlib
from selenium import webdriver


class Browser(contextlib.AbstractContextManager):

    def __init__(self, **options):
        self._start(**options)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._quit()

    def _start(self, **options):
        """
        Opens a new WebDriver instance
        """
        self._driver = webdriver.Firefox(**options)
        self._driver.maximize_window()

    def _quit(self):
        self._driver.quit()
