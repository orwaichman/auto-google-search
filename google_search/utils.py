import logging
import numpy.random
import re
import time
import urllib.parse

from .const import GoogleRegex

NORMAL_MIN_COEFFICIENT = 0.2  # determines minimal value proportionally to value
NORMAL_SCALE_COEFFICIENT = 0.3  # determines scale proportionally to value


def non_bot_delay_exec(seconds, scale=None, min_value=None):
    """
    Randomly delays execution of a function based on normal distribution. For more details on argument see random_wait()

    Args:
        seconds (float): Value around which the random delay will be determined
        scale (float):
        min_value (float):
    """

    def decorator(func):
        def inner(*args, **kwargs):
            logging.debug(f'Delayed execution of "{func.__name__}" for {random_wait(seconds, scale, min_value)}s')
            return func(*args, **kwargs)

        return inner

    return decorator


def random_wait(seconds, scale=None, min_value=None):
    """
    Randomly sleeps, based on normal distribution

    Args:
        seconds (float): Value around which the random delay will be determined
        scale (float): Scale (sigma) of the distribution. By default, scales proportionally to the given value.
                       f.e. scale of 0.6 means around +- 1 second.
        min_value (float): Minimal value of delay. This is to prevent negative or very small values.
                           By default, scales proportionally to the given value.
    """
    if not scale:
        scale = NORMAL_SCALE_COEFFICIENT * seconds
    if not min_value:
        min_value = NORMAL_MIN_COEFFICIENT * seconds

    seconds_to_wait = numpy.random.normal(seconds, scale)
    if seconds_to_wait < min_value:
        seconds_to_wait = abs(min_value - seconds_to_wait) + min_value

    time.sleep(seconds_to_wait)

    return seconds_to_wait


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
