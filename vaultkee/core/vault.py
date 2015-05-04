#!/usr/bin/python

import urllib2
import json

def get(url, endpoint, token):
    url = sanitize_url(url)
    opener = urllib2.build_opener()
    opener.addheaders.append(('Cookie', 'token=' + token))
    f = opener.open(url + endpoint)
    contents = f.read()

    data = json.loads(contents)
    return data


def sanitize_url(url):
    url = str(url)
    if not url.endswith('/'):
        url += '/'
    if not url.endswith('v1/'):
        url += 'v1/'

    return url


def get_mounts(url, token):
    contents = get(url, '/sys/mounts', token)
    return contents


if __name__ == "__main__":
    get_mounts("http://127.0.0.1:8200/v1/", "ea75ca7f-0b8f-d618-83e7-6cfac18de178")
