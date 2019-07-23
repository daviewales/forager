#!/usr/bin/env python3

from requests_html import HTMLSession
from pprint import pprint
from time import sleep
import sys

# If getting timeout errors, check this workaround:
# https://github.com/oldani/requests-html/issues/278#issuecomment-476950656


def scrape(base_url, sub_url_css_selector, timeout=10, render_wait=2):
    session = HTMLSession()

    r = session.get(base_url, timeout=timeout)
    r.html.render(timeout=timeout, wait=render_wait)

    selection = r.html.find(sub_url_css_selector)

    urls = []
    for item in selection:
        for link in item.links:
            urls.append(base_url + link)

    return urls

def forage(url, keywords, timeout=10, render_wait=2):
    session = HTMLSession()
    r = session.get(url, timeout=timeout)
    r.html.render(timeout=timeout, wait=render_wait)

    for keyword in keywords:
        if keyword in r.html.text:
            print('Found keyword {} at url {}'.format(keyword, url))

def progress(wait, steps=10):
    print('Waiting {:.1f} seconds'.format(wait), end=' ')
    for i in range(steps):
        sys.stdout.flush()
        print('.', end='')
        sleep(wait / steps)
    print('')

def main():
    import random
    import json
    from pathlib import Path

    VISITED_URL_FILE = Path('~/.forager_checked_urls.json').expanduser()
    BASE_URL = 'http://plazabookexchange.coffeecup.com/stream.html'
    SUB_URL_CSS_SELECTOR = '.sdrive-stream-post-title'
    KEYWORDS = ['Office', 'Harry Potter']
    MIN_FETCH_WAIT = 1
    MAX_FETCH_WAIT = 3
    TIMEOUT = 30
    RENDER_WAIT = 2

    try:
        with VISITED_URL_FILE.open() as file:
            visited_urls = json.load(file)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        visited_urls = []

    print('Scraping for new urls at {}'.format(BASE_URL))
    urls = scrape(BASE_URL, SUB_URL_CSS_SELECTOR, timeout=TIMEOUT, render_wait=RENDER_WAIT)

    new_urls = [url for url in urls if url not in visited_urls]
    print('{} new urls found!'.format(len(new_urls)))

    for url_number, url in enumerate(new_urls):
        print()
        print('Checking url {} of {}'.format(url_number + 1, len(urls)))
        forage(url, KEYWORDS, timeout=TIMEOUT, render_wait=RENDER_WAIT)
        visited_urls.append(url)
        wait = random.uniform(MIN_FETCH_WAIT, MAX_FETCH_WAIT)
        progress(wait, steps=10)

    with VISITED_URL_FILE.open('w') as file:
        file.write(json.dumps(visited_urls, indent=4))


if __name__ == '__main__':
    main()
