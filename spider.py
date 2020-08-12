import json
import random

import requests
from lxml import etree

GITHUB_URL = 'https://github.com/'
REPOSITORY = GITHUB_URL + 'trending/'
DEVELOPER = REPOSITORY + 'developers/'
USER_AGENTS = [
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; "
    "SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; "
    "SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
    "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; "
    "Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; "
    "Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; "
    ".NET CLR 2.0.50727; Media Center PC 6.0)",
    "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; "
    "Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; "
    ".NET CLR 3.5.30729; .NET CLR 3.0.30729; "
    ".NET CLR 1.0.3705; .NET CLR 1.1.4322)",
    "Mozilla/4.0 (compatible; MSIE 7.0b; "
    "Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; "
    "InfoPath.2; .NET CLR 3.0.04506.30)",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) "
    "AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) "
    "Arora/0.3 (Change: 287 c9dfb30)",
    "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ "
    "(KHTML, like Gecko, Safari/419.3) Arora/0.6",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; "
    "rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) "
    "Gecko/20080705 Firefox/3.0 Kapiko/3.0",
    "Mozilla/5.0 (X11; Linux i686; U;) "
    "Gecko/20070322 Kazehakase/0.4.5",
    "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) "
    "Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 "
    "(KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) "
    "AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
    "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) "
    "Presto/2.9.168 Version/11.52"
]
HEADER = {'User-Agent': random.choice(USER_AGENTS)}
TIMEOUT = 15
NO_RESULT = {
    'count': 0,
    'msg': 'Unavailable',
    'items': [],
}


def get_trending(url: str, params: dict = None) -> dict:
    html = get_html(url, params)
    if html is not None:
        is_blank = has_trending(html)
        if not is_blank:
            if url.find(DEVELOPER) >= 0:
                return parse_developer(html)
            else:
                return parse_repo(html)
        else:
            return NO_RESULT
    else:
        return NO_RESULT


def parse_repo(html) -> dict:
    items = []
    articles = html.xpath('//article')
    for article in articles:
        item = {'repo': article.xpath('./h1/a/@href')[0][1:]}
        item['repo_link'] = GITHUB_URL + item['repo']
        tmp = article.xpath('./p/text()')
        item['desc'] = tmp[0].replace(
            '\n', '').strip() if len(tmp) > 0 else ''
        tmp = article.xpath('./div[last()]/span[1]/span[2]/text()')
        item['lang'] = tmp[0].replace(
            '\n', '').strip() if len(tmp) > 0 else ''
        tmp = article.xpath('./div[last()]/a[1]/text()')
        item['stars'] = "".join(tmp).replace(' ', '').replace('\n', '')
        tmp = article.xpath('./div[last()]/a[2]/text()')
        item['forks'] = "".join(tmp).replace(' ', '').replace('\n', '')
        tmp = article.xpath('./div[last()]/span[3]/text()')
        item['added_stars'] = "".join(tmp).replace('\n', '').strip()
        item['avatars'] = article.xpath('./div[last()]/span[2]/a/img/@src')
        items.append(item)
    return {
        'count': len(items),
        'msg': 'suc',
        'items': items
    }


def parse_developer(html) -> dict:
    items = []
    articles = html.xpath('//article')
    for article in articles:
        if len(article.xpath('./div[2]/div[1]/div[1]/h1/a/@href')) == 0:
            continue
        user = article.xpath('./div[2]/div[1]/div[1]/h1/a/@href')[0][1:]
        item = {'user': user}
        item['user_link'] = GITHUB_URL + item['user']
        item['full_name'] = article.xpath(
            './div[2]/div[1]/div[1]/h1/a/text()')[0][1:].replace('\n', '').strip()
        item['developer_avatar'] = article.xpath('./div[1]/a/img/@src')[0]
        items.append(item)
    return {
        'count': len(items),
        'msg': 'suc',
        'items': items
    }


def has_trending(html):
    blank = html.xpath('//div[contains(@class,"blankslate")]')
    if blank or len(blank) > 0:
        return html.xpath('string(//div[contains(@class,"blankslate")]/h3)') \
            .replace('\n', '').strip()
    else:
        return None


def get_html(url: str, params: dict = None):
    try:
        if params is not None:
            url = "{0}?since={1}".format(url, params.get('since'))
        response = requests.get(url, headers=HEADER, timeout=TIMEOUT)
        return etree.HTML(response.text)
    except Exception:
        return None
