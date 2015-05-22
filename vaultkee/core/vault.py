#!/usr/bin/python

import urllib2
import requests
import json
import logging

# Set up logging
logger = logging.getLogger(__name__)

def get(url, endpoint, token):
    url = sanitize_url(url)
    logger.debug("Fetching %s%s" % (url, endpoint))
    opener = urllib2.build_opener()
    opener.addheaders.append(('Cookie', 'token=' + token))
    f = opener.open(url + endpoint)
    contents = f.read()

    data = json.loads(contents)
    return data


def sanitize_url(url):
    url = str(url)
    logger.debug("Sanitizing URL: '%s'" % url)
    if not url.endswith('/'):
        url += '/'
    if not url.endswith('v1/'):
        url += 'v1/'

    return url


def get_mounts(url, token):
    endpoint = '/sys/mounts'
    logger.debug("Fetching available mounts from '%s%s'" % (str(url), endpoint))
    contents = get(url, '/sys/mounts', token)
    return contents


def get_listings(url):
    logger.debug("Fetching list of secrets from '%s'" % str(url))
    response = urllib2.urlopen(str(url))
    contents = response.read()
    data = json.loads(contents)

    return data


def write_secret(url, token, path, data):
    url = sanitize_url(url)
    logger.debug("Writing secret to '%s%s'" % (url, path))
    r = requests.put(url + path, data=json.dumps(data), cookies={"token": token})

    if r.text:
        data = json.loads(r.text)
    else:
        data = ""
    return data


def delete_secret(url, token, path):
    url = sanitize_url(url)
    logger.debug("Deleting secret at '%s%s'" % (url, path))
    r = requests.delete(url + path, cookies={"token": token})

    return r


def read_secret(url, token, path):
    url = sanitize_url(url)
    logger.debug("Reading secret from '%s%s'" % (url, path))
    r = requests.get(url + path, cookies={"token": token})

    if r.text:
        data = json.loads(r.text)
    else:
        data = ""
    return data


def lookup_self(url, token):
    endpoint = '/auth/token/lookup-self'
    logger.debug("Looking up token: '%s%s'" % (url, endpoint))
    contents = get(url, endpoint, token)
    return contents


if __name__ == "__main__":
    print get_mounts("http://127.0.0.1:8200/v1/", "0d366ace-b059-dbd4-30ce-6f9dbc763294")
    print lookup_self("http://127.0.0.1:8200/v1/", "0d366ace-b059-dbd4-30ce-6f9dbc763294")
    print write_secret("http://127.0.0.1:8200/v1/", "0d366ace-b059-dbd4-30ce-6f9dbc763294", "secret/ididnt/exist/before", {"value": "test"})
    print read_secret("http://127.0.0.1:8200/v1/", "0d366ace-b059-dbd4-30ce-6f9dbc763294", "secret/ididnt/exist/before")
