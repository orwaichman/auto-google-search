import requests
from lxml import html
import urllib.parse

from const import GOOGLE_SEARCH_URL


class BasicSearcher(object):
    """
    BasicSearcher is a prototype of an object with actions related to Google search
    """
    def __init__(self):
        pass

    def _get_html(self, url):
        response = requests.get(url)
        response.raise_for_status()  # If status code not ok, raises requests.exceptions.HTTPError

        return html.fromstring(response.text)

    def search(self, text):
        """
        Performs a simple Google search (without Selenium).
        Args:
            text (str): Text to search

        Returns:
            lxml.html.HtmlElement:
        """
        return self._get_html(GOOGLE_SEARCH_URL.format(text=urllib.parse.quote_plus(text)))
