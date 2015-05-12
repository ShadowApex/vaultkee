#!/usr/bin/python

import urllib2
import requests
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


def get_listings(url):
    response = urllib2.urlopen(str(url))
    contents = response.read()
    data = json.loads(contents)

    return data


def write_secret(url, token, path, data):
    url = sanitize_url(url)
    r = requests.put(url + path, data=json.dumps(data), cookies={"token": token})

    if r.text:
        data = json.loads(r.text)
    else:
        data = ""
    return data


def delete_secret(url, token, path):
    url = sanitize_url(url)
    r = requests.delete(url + path, cookies={"token": token})

    print r.__dict__


def read_secret(url, token, path):
    url = sanitize_url(url)
    r = requests.get(url + path, cookies={"token": token})

    if r.text:
        data = json.loads(r.text)
    else:
        data = ""
    return data


def lookup_self(url, token):
    contents = get(url, '/auth/token/lookup-self', token)
    return contents


if __name__ == "__main__":
    print get_mounts("http://127.0.0.1:8200/v1/", "0d366ace-b059-dbd4-30ce-6f9dbc763294")
    print lookup_self("http://127.0.0.1:8200/v1/", "0d366ace-b059-dbd4-30ce-6f9dbc763294")
    print write_secret("http://127.0.0.1:8200/v1/", "0d366ace-b059-dbd4-30ce-6f9dbc763294", "secret/ididnt/exist/before", {"value": "test"})
    print read_secret("http://127.0.0.1:8200/v1/", "0d366ace-b059-dbd4-30ce-6f9dbc763294", "secret/ididnt/exist/before")
