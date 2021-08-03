import requests
import urllib.parse
from lxml import html

from background_browser import BackgroundBrowser
from basic_searcher import BasicSearcher
from const import NON_BOT_USER_AGENT
from utils import random_wait

# Artificial delay to try to avoid being recognized as bots. Preferable use is before each GET request in the browser
ARTIFICIAL_AVERAGE_DELAY = 1.5  # Seconds


class Searcher(BackgroundBrowser, BasicSearcher):
    def _get(self, url):
        random_wait(ARTIFICIAL_AVERAGE_DELAY)
        return self._non_delayed_get(url)

    def _non_delayed_get(self, url):
        # If url starts with '/' we stay at current host and adjust the request accordingly
        if self._host and url.startswith('/'):
            url = self._host + url

        # Performs the request
        response = requests.get(url, headers={'user-agent': NON_BOT_USER_AGENT})
        response.raise_for_status()  # If status code not ok, raises requests.exceptions.HTTPError

        # Updates attributes
        parsed_uri = urllib.parse.urlparse(url)
        self._host = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)
        self._html = html.fromstring(response.text)
