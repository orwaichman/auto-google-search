import pytest

from const import IMAGES_SECTION
from tests import TestingSearcher


@pytest.mark.dependency()
def test_search():
    with TestingSearcher() as s:
        s.search('google')


@pytest.mark.dependency(depends=['test_search'])
def test_go_to_search_section():
    with TestingSearcher() as s:
        s.go_to_search_section(IMAGES_SECTION)


@pytest.mark.dependency(depends=['test_go_to_search_section'])
def test_scan_image_results():
    with TestingSearcher() as s:
        results = list(s.scan_image_results(max_iterations=4))
        assert len(results) == 4