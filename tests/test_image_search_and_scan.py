import pytest

from tests import TestingSearcher


@pytest.mark.dependency()
def test_image_search():
    with TestingSearcher() as s:
        s.search_image('https://res.feednews.com/assets/v2/59c118b47675e42a9f6d9f97a110a614?width=1280&height=720&quality=hq&category=us_Knowledge')


@pytest.mark.dependency(depends=['test_image_search'])
def test_navigate_to_identical_images():
    with TestingSearcher() as s:
        s.navigate_to_identical_images()


@pytest.mark.dependency(depends=['test_navigate_to_identical_images'])
def test_scan_image_results():
    with TestingSearcher() as s:
        results = list(s.scan_image_results(max_iterations=2))
        assert len(results) == 2
