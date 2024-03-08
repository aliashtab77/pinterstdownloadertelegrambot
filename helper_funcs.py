from fake_useragent import UserAgent
import requests
from pyquery import PyQuery as pq


def pintopinterst(url_path):
    ua = UserAgent()
    UA = ua.chrome
    SHARE_SESSION = requests.Session()
    SHARE_SESSION.headers = {
        # 'Host': 'www.pinterest.com',
        'User-Agent': UA,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'DNT': '1',
        'Upgrade-Insecure-Requests': '1',
        'Connection': 'keep-alive'
    }
    r = SHARE_SESSION.get(url_path, timeout=(15, 15))
    if (r.status_code == 200) and '/sent' in r.url:
        arg_path = r.url.split('/sent')[0]
        return arg_path
    else:
        return False


def get_download_url(link):
    # Make request to website
    post_request = requests.post('https://www.expertsphp.com/download.php', data={'url': link})

    # Get content from post request
    request_content = post_request.content
    str_request_content = str(request_content, 'utf-8')
    download_url = pq(str_request_content)('table.table-condensed')('tbody')('td')('a').attr('href')
    return download_url