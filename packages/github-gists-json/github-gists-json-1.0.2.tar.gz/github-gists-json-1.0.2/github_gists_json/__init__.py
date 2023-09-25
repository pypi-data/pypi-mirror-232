import os
from urllib.parse import parse_qs, urlparse

from linkheader_parser import parse
import requests


def get_data(login=None):
    url = 'https://api.github.com/gists'
    if login:
        url = 'https://api.github.com/users/%s/gists' % login
    parameters = dict(per_page=100)
    url = url+'?' + '&'.join(map(lambda i:'%s=%s' % i,parameters.items()))
    data = []
    if "GITHUB_TOKEN" not in os.environ:
        raise ValueError('GITHUB_TOKEN UNKNOWN')
    headers = {
        "Authorization": "Bearer %s" % os.getenv("GITHUB_TOKEN"),
    }
    while True:
        r = requests.get(url,headers=headers)
        if r.status_code!=200:
            raise ValueError(r.text)
        data+=r.json()
        if 'Link' in r.headers:
            parsed_links = parse(r.headers['Link'])
            if 'next' not in parsed_links:
                break
            url = parsed_links['next']['url']
    return list(map(lambda d:{i:d[i] for i in d if '_url' not in i and i!='owner'},data))

