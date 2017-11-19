import argparse
import urllib.parse

import logging
import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('site-map-generator')


class GenerateSiteMap:
    def __init__(self, site_url):
        self.site_url = site_url
        self.crawled_urls = []
        self.urls_to_crawl = [site_url]
        self.domain = urllib.parse.urlparse(self.site_url).netloc

    def crawl(self):
        if not self.urls_to_crawl:
            self.write_site_map()
            return

        url = self.urls_to_crawl.pop()
        logger.info('On URL: {}'.format(url))
        try:
            content = self.fetch_url(url)
        except:
            logger.warning('Error occurred while processing URL: {}'.format(url))
            self.crawled_urls.append(url)
            self.crawl()
            return

        self.crawled_urls.append(url)
        soup = BeautifulSoup(content, 'html.parser')
        for link in soup.find_all('a', {'href': True}):
            if not link:
                continue

            url = self.get_parsed_url(link['href'])
            if url and url not in self.crawled_urls and url not in self.urls_to_crawl:
                self.urls_to_crawl.append(url)

        self.crawl()

    def get_parsed_url(self, url):
        if url.startswith('/'):
            return urllib.parse.urljoin(self.site_url, url)

        if url in ['#', '/'] or not url.startswith(self.site_url):
            return None

        return url

    def write_site_map(self):
        file_name = 'sitemap-{}.xml'.format(self.domain)
        with open(file_name, 'w') as f:
            f.write('<?xml version="1.0" encoding="utf-8"?>\n')
            f.write(
                '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"'
                ' xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
                'xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9 '
                'http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd">\n')
            url_str = '<url><loc>{}</loc></url>\n'
            for url in self.crawled_urls:
                f.write(url_str.format(url))
            f.write('</urlset>')

    def fetch_url(self, url):
        response = requests.get(url)
        response.raise_for_status()
        return response.content


def main():
    parser = argparse.ArgumentParser(description='Generate site map of the provided site URL')
    parser.add_argument('-u', '--url', help='URL of the site')
    args = parser.parse_args()
    gsm = GenerateSiteMap(site_url=args.url)
    gsm.crawl()


if __name__ == '__main__':
    main()
