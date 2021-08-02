import abc

from const import WEBDRIVER_PATH
from selenium_searcher import SeleniumSearcher
from searcher import Searcher


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class SingletonMeta(Singleton, abc.ABCMeta):
    pass


# Modifying SeleniumSearcher used for testing to be a single instance class that can only be closed explicitly
class TestingSeleniumSearcher(SeleniumSearcher, metaclass=SingletonMeta):
    def __init__(self):
        super().__init__(executable_path=WEBDRIVER_PATH)

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class TestingSearcher(Searcher, metaclass=SingletonMeta):
    pass
