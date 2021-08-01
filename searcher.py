import itertools
import time
import urllib.parse

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from basic_searcher import BasicSearcher
from browser import Browser
from const import GOOGLE_URL, GOOGLE_SEARCH_URL, GOOGLE_IMAGE_URL_SEARCH_URL, GoogleXpaths
from parse_utils import parse_image_result_site_url, parse_image_result_image_url
from result import ImageResult

MAX_DELAY = 7  # Seconds
MAX_ATTEMPTS = 10


class Searcher(Browser, BasicSearcher):
    """
    Searcher can perform miscellaneous web scraping actions in Google search, using Selenium webdriver
    """

    def __init__(self, **options):
        Browser.__init__(self, **options)
        BasicSearcher.__init__(self)

    def _start(self, **options):
        super(Searcher, self)._start(**options)
        self._driver.get(GOOGLE_URL)

    def _wait_for_elements(self, xpath):
        """
        Waits for elements to load and fetches them

        Args:
            xpath (str):

        Returns:
            list[WebElement]
        """
        try:
            WebDriverWait(self._driver, MAX_DELAY).until(
                EC.presence_of_element_located((By.XPATH, xpath)))
            return self._driver.find_elements_by_xpath(xpath)
        except TimeoutException:
            return []

    def _wait_for_element(self, xpath):
        elements = self._wait_for_elements(xpath)
        if not elements:
            raise NoSuchElementException(f'Could not find element "{xpath}"')
        return elements[0]

    def search(self, text):
        """
        Performs a simple search

        Args:
            text (str): Text to search
        """
        self._driver.get(GOOGLE_SEARCH_URL.format(text=urllib.parse.quote_plus(text)))

    def search_image(self, image_url):
        """
        Performs an image search from url

        Args:
            image_url (str): Image url to search
        """
        self._driver.get(GOOGLE_IMAGE_URL_SEARCH_URL.format(image_url=urllib.parse.quote_plus(image_url)))

    def go_to_search_section(self, name):
        """
        Navigates to a section (Images, Videos, News...) of a search results page

        Notes:
            * Assumes driver is in search results page
            * Also supports navigating to sections under 'More', Although we cannot extract results from them
            * Use of built-in constants for name is preferable

        Args:
            name (Union[str, tuple]): Name of the section, use tuple for multiple tries

        Raises:
            NoSuchElementException: If the section was not found
        """
        possible_section_names = (name,) if not isinstance(name, tuple) else name
        sections = self._wait_for_elements(GoogleXpaths.SECTIONS_LINKS)

        for section in sections:
            for section_name in possible_section_names:
                if section_name.lower() in section.text.lower():
                    self._driver.get(section.get_attribute('href'))
                    return

        raise NoSuchElementException(f'Section {name} not found')

    def navigate_to_identical_images(self):
        """
        Navigates to image search results page of identical images to the one that was searched

        Notes:
            * Assumes driver is in a search results page for image url
            * Google might offer separation to size categories, we choose all sizes

        Raises:
            NoSuchElementException: If the option was not available for current search
        """
        try:
            self._driver.find_element_by_xpath(GoogleXpaths.Search.ALL_SIZES_LINK).click()
        except NoSuchElementException:
            raise NoSuchElementException('There\'s no option for other sizes of image')

    def navigate_to_similar_images(self):
        """
        Navigates to image search results page of visually similar images to the one that was searched

        Notes:
            * Assumes driver is in a search results page for image url

        Raises:
            NoSuchElementException: If the option was not available for current search
        """
        try:
            self._driver.find_element_by_xpath(GoogleXpaths.Search.SIMILAR_IMAGES_LINK).click()
        except NoSuchElementException:
            raise NoSuchElementException('There\'s no option for visually similar images')

    def scan_search_results(self, max_iterations: int = 10):
        """
        Parses standard search results

        Notes:
            * Assumes driver is in search results page
            * Assigning None to max_iterations is not recommended as search result count is often very high

        Args:
            max_iterations (int): Limit for number of results, None for no artificial limit

        Yields:
            Selenium WebElements
        """
        counter = 0

        # Loop on pages, iterates ceil(max_iterations/10) times, or infinite if specified so
        for _ in itertools.islice(itertools.count(), 0, max_iterations, 10):
            current_page_results = self._wait_for_elements(GoogleXpaths.Search.RESULTS_DIVS)

            # Collect all results in page unless max_iterations limits that
            num_of_results_from_page = min(10, max_iterations - counter)
            for raw_result in current_page_results[:num_of_results_from_page]:
                yield self._parse_search_result(raw_result)
            counter += num_of_results_from_page

            # Navigating to the next page, or stopping if there isn't any
            try:
                self._driver.find_element_by_xpath(GoogleXpaths.Search.NEXT_PAGE_LINK).click()
            except NoSuchElementException:
                break

    @staticmethod
    def _parse_search_result(raw_result):
        # Not implemented
        return raw_result

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
            NoSuchElementException: If element structure is not as expected
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
            raise NoSuchElementException(
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

    def scan_image_results(self, max_iterations: int = None):
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
        except NoSuchElementException:
            return  # No results found

        previous_result = None
        for i in itertools.islice(itertools.count(), 0, max_iterations):
            result_div = self._driver.find_element_by_xpath(GoogleXpaths.ImageSearch.OPENED_RESULT_DIV)
            self._wait_until_image_fully_loaded()
            result = self._parse_opened_image_result(result_div)

            # We need to make sure that we don't parse the last image result multiple times. It might happen because
            # it takes some time for the 'next' button to be disabled in the UI
            if result == previous_result:
                break

            yield self._parse_opened_image_result(result_div)

            next_button = result_div.find_element_by_xpath(GoogleXpaths.ImageSearch.OpenedResult.NEXT_BUTTON_RELATIVE)
            # Check if reached to the end
            if next_button.get_attribute('disabled') == 'true':
                break

            if max_iterations and max_iterations > i + 1:
                next_button.click()
            previous_result = result

    def _wait_until_image_fully_loaded(self):
        """
        Waits for opened image result's image src to be loaded
        """
        for _ in range(MAX_ATTEMPTS):
            image_url = self._driver.find_element_by_xpath(
                GoogleXpaths.ImageSearch.OpenedResult.IMAGE_RELATIVE).get_attribute('src')
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
