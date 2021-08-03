import itertools
import json
import re
import urllib.parse

from basic_browser import BasicBrowser
from const import GOOGLE_SEARCH_URL, GOOGLE_IMAGE_URL_SEARCH_URL, GoogleRegex, GoogleXpaths
from exceptions import NoSuchElement
from result import ImageResult


class BasicSearcher(BasicBrowser):
    """
    BasicSearcher is a prototype of an object with actions related to Google search
    """

    def search(self, text):
        """
        Performs a simple Google search (without Selenium).
        Args:
            text (str): Text to search

        Returns:
            lxml.html.HtmlElement:
        """
        self._non_delayed_get(GOOGLE_SEARCH_URL.format(text=urllib.parse.quote_plus(text)))

    def search_image(self, image_url):
        """
        Performs an image search from url

        Args:
            image_url (str): Image url to search
        """
        self._non_delayed_get(GOOGLE_IMAGE_URL_SEARCH_URL.format(image_url=urllib.parse.quote_plus(image_url)))

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
            NoSuchElement: If the section was not found
        """
        possible_section_names = (name,) if not isinstance(name, tuple) else name
        sections = self._find_elements_by_xpath(GoogleXpaths.SECTIONS_LINKS)

        for section in sections:
            for section_name in possible_section_names:
                if section_name.lower() in section.text.lower():
                    self._click_link(section)
                    return

        raise NoSuchElement(f'Section {name} not found')

    def navigate_to_identical_images(self):
        """
        Navigates to image search results page of identical images to the one that was searched

        Notes:
            * Assumes driver is in a search results page for image url
            * Google might offer separation to size categories, we choose all sizes

        Raises:
            NoSuchElement: If the option was not available for current search
        """
        try:
            self._click_link(self._find_element_by_xpath(GoogleXpaths.Search.ALL_SIZES_LINK))
        except NoSuchElement:
            raise NoSuchElement('There\'s no option for other sizes of image')

    def navigate_to_similar_images(self):
        """
        Navigates to image search results page of visually similar images to the one that was searched

        Notes:
            * Assumes driver is in a search results page for image url

        Raises:
            NoSuchElement: If the option was not available for current search
        """
        try:
            self._click_link(self._find_element_by_xpath(GoogleXpaths.Search.SIMILAR_IMAGES_LINK))
        except NoSuchElement:
            raise NoSuchElement('There\'s no option for visually similar images')

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
            current_page_results = self._find_elements_by_xpath(GoogleXpaths.Search.RESULTS_DIVS)

            # Collect all results in page unless max_iterations limits that
            num_of_results_from_page = min(10, max_iterations - counter)
            for raw_result in current_page_results[:num_of_results_from_page]:
                yield self._parse_search_result(raw_result)
            counter += num_of_results_from_page

            # Navigating to the next page, or stopping if there isn't any
            try:
                self._click_link(self._find_element_by_xpath(GoogleXpaths.Search.NEXT_PAGE_LINK))
            except NoSuchElement:
                break

    @staticmethod
    def _parse_search_result(raw_result):
        # Not implemented
        return raw_result

    def scan_image_results(self, max_iterations: int = None):
        """
        Parses image search results by analyzing webpage's script

        Notes:
            * Assumes driver is in an image search results page

        Args:
            max_iterations (int): Limit for number of results, None for no artificial limit

        Yields:
            ImageResult:
        """
        script_text = self._get_element_text(self._find_element_by_xpath(GoogleXpaths.ImageSearch.RESULTS_JSON))
        return self._parse_image_results(script_text, max_iterations=max_iterations)

    @staticmethod
    def _parse_image_results(script_text, max_iterations: int = None):
        results_array_string = re.search(GoogleRegex.EXTRACT_IMAGE_RESULTS_FROM_JSON, script_text).group(0)
        raw_results = json.loads(results_array_string)
        if max_iterations is not None and len(raw_results) > max_iterations:
            raw_results = raw_results[:max_iterations]

        for raw_result in raw_results:
            yield BasicSearcher._parse_image_result_metadata(raw_result)

    @staticmethod
    def _parse_image_result_metadata(result):
        """
        Parse representation of image result taken from json
        Args:
            result (list):

        Returns:
            ImageResult:
        """
        title = None
        try:
            title = result[1][9]['2008'][1]
        except Exception:
            pass

        link = None
        try:
            link = result[1][9]['2003'][2]
        except Exception:
            pass

        site = None
        try:
            site = result[1][9]['183836587'][0]
        except Exception:
            pass

        image_url = None
        try:
            image_url = result[1][3][0]
        except Exception:
            pass

        return ImageResult(title=title,
                           site=site,
                           link=link,
                           image_url=image_url)
