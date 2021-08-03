import requests
import urllib.parse
from lxml import html

from basic_browser import BasicBrowser


class BackgroundBrowser(BasicBrowser):
    def __init__(self):
        super().__init__()
        self._html = None
        self._host = None

    def _non_delayed_get(self, url):
        # If url starts with '/' we stay at current host and adjust the request accordingly
        if self._host and url.startswith('/'):
            url = self._host + url

        # Performs the request, raises requests.HTTPError if status code is not OK
        response = requests.get(url)
        response.raise_for_status()

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
