class ResultBase(object):
    def __init__(self, title, site, link):
        self.title = title
        self.site = site
        self.link = link

    def __str__(self):
        return '\n '.join((f'Result',
                           f'title: {self.title}',
                           f'site name: {self.site}',
                           f'link: {self.link}'
                           ))

    def __eq__(self, other):
        return hasattr(other, 'link') and self.link == other.link


class ImageResult(ResultBase):
    def __init__(self, title, site, link, image_url):
        super().__init__(title, site, link)
        self.image_url = image_url

    def __str__(self):
        return '\n '.join((f'Image result',
                           f'title: {self.title}',
                           f'site name: {self.site}',
                           f'taken from: {self.link}',
                           f'url: {self.image_url}'))

    def __eq__(self, other):
        return super().__eq__(other) and hasattr(other, 'image_url') and self.image_url == other.image_url
