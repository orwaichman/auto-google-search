import re
import urllib.parse

from const import GoogleRegex


def extract_value_from_url(key, url):
    value = re.search(GoogleRegex.EXTRACT_URL_VALUE.format(key=key), url)
    if value:
        # If regex yielded result, take it
        return urllib.parse.unquote(value.group(0))
    # Otherwise returns None


def parse_image_result_site_url(raw_link):
    link = raw_link
    if raw_link.startswith('https://www.google.com/url'):
        link = extract_value_from_url(key='url', url=raw_link)

    return link


def parse_image_result_image_url(raw_link):
    if not raw_link.startswith('data:'):
        image_url = raw_link
        if raw_link.startswith('https://www.google.com/imgres'):
            image_url = extract_value_from_url(key='imgurl', url=raw_link)
            # This means we prefer None value over Google's url ref

        return image_url
