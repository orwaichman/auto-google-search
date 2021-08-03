import itertools
import time

from selenium.common.exceptions import NoSuchElementException

from basic_searcher import BasicSearcher
from selenium_browser import SeleniumBrowser
from const import GOOGLE_URL, GoogleXpaths
from exceptions import NoSuchElement
from utils import parse_image_result_site_url, parse_image_result_image_url, random_wait
from result import ImageResult

# Artificial delay to try to avoid being recognized as bots. Preferable use is before each GET request in the browser
ARTIFICIAL_AVERAGE_DELAY = 0.5  # Seconds.
# Other webdriver behavior configurations
MAX_DELAY = 7  # Seconds
MAX_ATTEMPTS = 10


class SeleniumSearcher(SeleniumBrowser, BasicSearcher):
    """
    SeleniumSearcher can perform miscellaneous web scraping actions in Google search, using Selenium webdriver
    """

    def __init__(self, **options):
        SeleniumBrowser.__init__(self, **options)
        BasicSearcher.__init__(self)

    def _start(self, **options):
        super(SeleniumSearcher, self)._start(**options)
        self._driver.get(GOOGLE_URL)

    def _get(self, url):
        random_wait(ARTIFICIAL_AVERAGE_DELAY)
        return self._non_delayed_get(url)

    def shallow_scan_image_results(self, max_iterations: int = None):
        """
        Parses image search results without opening them. Not recommended (details in the notes)

        Notes:
            * Assumes driver is in an image search results page
            * Due to Google's UI implementation, image results are assigned with the original
              image-src value only when clicking on them
            * Google only renders ~50 results before scrolling further down. This issue is not currently tackled

        Args:
            max_iterations (int): Limit for number of results, None for no artificial limit

        Yields:
            ImageResult:
        """
        raw_results = self._wait_for_elements(GoogleXpaths.ImageSearch.RESULTS_DIVS)

        for raw_result in itertools.islice(raw_results, 0, max_iterations):
            yield self._parse_image_result(raw_result)

    @staticmethod
    def _parse_image_result(raw_result):
        """
        Parses html element of a single image result

        Args:
            raw_result: Selenium web element that represents image result

        Returns:
            ImageResult: parsed result

        Raises:
            NoSuchElement: If element structure is not as expected
        """
        title = None
        site = None

        for title_xpath, site_xpath in GoogleXpaths.ImageSearch.Result.TITLE_AND_SITE_RELATIVE_OPTIONS:
            try:
                title = raw_result.find_element_by_xpath(title_xpath).text
                site = raw_result.find_element_by_xpath(site_xpath).text
                break
            except NoSuchElementException:
                continue

        if not title or not site:
            raise NoSuchElement(
                'Could not extract data from results due to change in Google\'s html structure')

        raw_link = raw_result.find_element_by_xpath(
            GoogleXpaths.ImageSearch.Result.SITE_LINK_RELATIVE).get_attribute('href')
        link = parse_image_result_site_url(raw_link)

        # Image result does not posses image url until clicked on, so it is not guaranteed that it was loaded
        raw_image_url = raw_result.find_element_by_xpath(
            GoogleXpaths.ImageSearch.Result.IMAGE_LINK_RELATIVE).get_attribute('href')
        image_url = parse_image_result_image_url(raw_image_url)

        return ImageResult(title=title,
                           site=site,
                           link=link,
                           image_url=image_url)

    def scan_image_results_by_opening(self, max_iterations: int = None):
        """
        Parses image search results by opening them

        Notes:
            * Assumes driver is in an image search results page

        Args:
            max_iterations (int): Limit for number of results, None for no artificial limit

        Yields:
            ImageResult:
        """
        try:
            # Clicks on the first result
            self._wait_for_element(GoogleXpaths.ImageSearch.RESULTS_DIVS).click()
        except NoSuchElement:
            return  # No results found

        previous_result = None
        for i in itertools.islice(itertools.count(), 0, max_iterations):
            result_div = self._find_element_by_xpath(GoogleXpaths.ImageSearch.OPENED_RESULT_DIV)
            self._wait_until_image_fully_loaded()
            result = self._parse_opened_image_result(result_div)

            # We need to make sure that we don't parse the last image result multiple times. It might happen because
            # it takes some time for the 'next' button to be disabled in the UI
            if result == previous_result:
                break

            yield self._parse_opened_image_result(result_div)

            next_button = result_div.find_element_by_xpath(GoogleXpaths.ImageSearch.OpenedResult.NEXT_BUTTON_RELATIVE)
            # Check if reached to the end
            if self._get_element_attribute(next_button, 'disabled') == 'true':
                break

            if max_iterations and max_iterations > i + 1:
                next_button.click()
            previous_result = result

    def _wait_until_image_fully_loaded(self):
        """
        Waits for opened image result's image src to be loaded
        """
        for _ in range(MAX_ATTEMPTS):
            image_url = self._get_element_attribute(self._find_element_by_xpath(
                GoogleXpaths.ImageSearch.OpenedResult.IMAGE_RELATIVE), 'src')
            if not image_url.startswith('data:'):
                return
            time.sleep(MAX_DELAY / MAX_ATTEMPTS)

    @staticmethod
    def _parse_opened_image_result(result_div):
        """
        Parses opened image result

        Args:
            result_div: Selenium web element that represents image result

        Returns:
            ImageResult: parsed result
        """
        title = result_div.find_element_by_xpath(
            GoogleXpaths.ImageSearch.OpenedResult.TITLE_RELATIVE).text

        site = result_div.find_element_by_xpath(
            GoogleXpaths.ImageSearch.OpenedResult.SITE_RELATIVE).text

        raw_link = result_div.find_element_by_xpath(
            GoogleXpaths.ImageSearch.OpenedResult.LINK_RELATIVE).get_attribute('href')
        link = parse_image_result_site_url(raw_link)

        raw_image_url = result_div.find_element_by_xpath(
            GoogleXpaths.ImageSearch.OpenedResult.IMAGE_RELATIVE).get_attribute('src')
        image_url = parse_image_result_image_url(raw_image_url)

        return ImageResult(title=title,
                           site=site,
                           link=link,
                           image_url=image_url)
