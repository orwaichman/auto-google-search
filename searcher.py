import contextlib
import requests
import urllib.parse
from lxml import html

from basic_searcher import BasicSearcher
from const import NON_BOT_USER_AGENT
from utils import random_wait

# Artificial delay to try to avoid being recognized as bots. Preferable use is before each GET request in the browser
ARTIFICIAL_AVERAGE_DELAY = 1.5  # Seconds


class Searcher(BasicSearcher, contextlib.AbstractContextManager):
    def __init__(self):
        super().__init__()
        self._html = None
        self._host = None

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def _get(self, url):
        random_wait(ARTIFICIAL_AVERAGE_DELAY)
        return self._non_delayed_get(url)

    def _non_delayed_get(self, url):
        # If url starts with '/' we stay at current host and adjust the request accordingly
        if self._host and url.startswith('/'):
            url = self._host + url

        # Performs the request, raises requests.HTTPError if status code is not OK
        response = requests.get(url, headers={'user-agent': NON_BOT_USER_AGENT})
        response.raise_for_status()  # If status code not ok, raises requests.exceptions.HTTPError

        # Updates attributes
        parsed_uri = urllib.parse.urlparse(url)
        self._host = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)
        self._html = html.fromstring(response.text)

    def _find_elements_by_xpath(self, xpath):
        return self._html.xpath(xpath)

    @staticmethod
    def _get_element_attribute(element, attr):
        return element.attrib[attr]

    @staticmethod
    def _get_element_text(element):
        return element.text_content()
