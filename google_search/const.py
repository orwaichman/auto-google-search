# -*- coding: utf-8 -*-


WEBDRIVER_PATH = r'C:\OtherPrograms\geckodriver.exe'  # Be sure to install Geckodriver (or any other driver, just update the code accordingly)

GOOGLE_URL = 'https://www.google.com'
GOOGLE_SEARCH_URL = f'{GOOGLE_URL}/search?q={{text}}'
GOOGLE_IMAGE_URL_SEARCH_URL = f'{GOOGLE_URL}/searchbyimage?image_url={{image_url}}'
NON_BOT_USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'

IMAGES_SECTION = ('Images', 'תמונות')
NEWS_SECTION = ('News', 'חדשות')
VIDEOS_SECTION = ('Videos', 'סרטונים')


class GoogleXpaths:
    # Common xpaths to homepage, search results page and image results page
    _SEARCH_FORM = '//form[@action="/search"]'
    SEARCH_BAR = '//input[@maxlength]'
    SEARCH_BUTTON = f'{_SEARCH_FORM}//input[contains(@value, "Google")][2]'
    SECTIONS_LINKS = '//*[@id="hdtb-msb"]//a'

    class Search:
        _CARD_SECTION = '//div[contains(@class, "card-section")]'
        SEARCH_BY_IMAGE_LINK = '//a[contains(@href, "/searchbyimage")]'
        IMAGE_SIZE_LABEL = f'{_CARD_SECTION}//span[contains(text(), "×")]'
        ALL_SIZES_LINK = f'{_CARD_SECTION}//a[contains(@href, "/search")][1]'
        SIMILAR_IMAGES_LINK = '//*[@id="rso"]//g-section-with-header//title-with-lhs-icon'

        RESULTS_DIVS = '//*[@id="rso"]/div[contains(@class, "g")]'  # Does not cover Google News results
        NEWS_RESULTS_DIVS = '//*[@id="rso"]//g-card'
        NEXT_PAGE_LINK = '//*[@id="pnnext"]'

        class Result:
            pass  # add Xpaths for parsing standard search results

    class ImageSearch:
        RESULTS_DIVS = '//*[@id="islrg"]/div[1]/div'
        OPENED_RESULT_DIV = '//*[@id="islsp"]'  # Only relevant if result was opened
        RESULTS_JSON = '''//*[@id="yDmH0d"]/script[starts-with(text(), "AF_initDataCallback({key: 'ds:1'")]'''

        class Result:
            IMAGE_LINK_RELATIVE = './/a[1]'
            SITE_LINK_RELATIVE = './/a[2]'
            TITLE_AND_SITE_RELATIVE_OPTIONS = (
                (f'{SITE_LINK_RELATIVE}/div[1]', f'{SITE_LINK_RELATIVE}/div[2]/span'),  # For UI in Hebrew
                (SITE_LINK_RELATIVE, f'{SITE_LINK_RELATIVE}/div[1]'))  # For UI in English

        class OpenedResult:
            # Notice that these are weak xpaths - they depend on class names
            _DISPLAYED_PANEL_RELATIVE = './/div[contains(@class, "BIB1wf")]'
            IMAGE_RELATIVE = f'{_DISPLAYED_PANEL_RELATIVE}//a/img'
            IMAGE_DIMENSIONS_RELATIVE = f'{_DISPLAYED_PANEL_RELATIVE}//a/span'
            LINK_RELATIVE = f'{_DISPLAYED_PANEL_RELATIVE}//a[@rel]'
            NEXT_BUTTON_RELATIVE = f'{_DISPLAYED_PANEL_RELATIVE}//a[contains(@class, "gvi3cf")]'
            SITE_RELATIVE = f'{_DISPLAYED_PANEL_RELATIVE}//div[contains(@class, "S4aXnb")]'
            TITLE_RELATIVE = f'{_DISPLAYED_PANEL_RELATIVE}//div[contains(@class, "eYbsle")]'


class GoogleRegex:
    EXTRACT_URL_VALUE = r'(?<=[?&]{key}=)[^&]*(?=&)'  # Invalid as regex by itself
    URL_VALUE_FROM_URL = EXTRACT_URL_VALUE.format(key='url')
    IMGURL_VALUE_FROM_URL = EXTRACT_URL_VALUE.format(key='imgurl')
    EXTRACT_IMAGE_RESULTS_FROM_JSON = r'(?<=\["GRID_STATE0",null,)\[.*\](?=,"","","",)'
