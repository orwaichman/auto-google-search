import pytest

from google_search.const import IMAGES_SECTION
from tests import TestingSeleniumSearcher


@pytest.mark.dependency()
def test_search():
    with TestingSeleniumSearcher() as s:
        s.search('google')


@pytest.mark.dependency(depends=['test_search'])
def test_go_to_search_section():
    with TestingSeleniumSearcher() as s:
        s.go_to_search_section(IMAGES_SECTION)


@pytest.mark.dependency(depends=['test_go_to_search_section'])
def test_scan_image_results_by_opening():
    with TestingSeleniumSearcher() as s:
        results = list(s.scan_image_results_by_opening(max_iterations=4))
        assert len(results) == 4
