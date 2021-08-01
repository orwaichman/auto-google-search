from searcher import Searcher
from const import WEBDRIVER_PATH


def main():
    # Example of usage
    with Searcher(executable_path=WEBDRIVER_PATH) as s:
        s.search_image('https://img-9gag-fun.9cache.com/photo/aO3Od02_460swp.webp')
        s.navigate_to_identical_images()
        for result in s.scan_image_results(16):
            print(result)


if __name__ == '__main__':
    main()
