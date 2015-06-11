#!/usr/bin/python
import urllib2
import requests
import json
import logging
import os

# Set up logging
logger = logging.getLogger(__name__)

# Get the path of our cacert.pem file for verifying SSL
module_path = os.path.dirname(os.path.realpath(__file__))
cert_locations = [os.path.realpath(os.path.join(module_path, "..")),
                  os.path.realpath(os.path.join(os.path.join(module_path, ".."), ".."))]
for cert_dir in cert_locations:
    cert_file = os.path.join(cert_dir, "cacert.pem")
    if os.path.isfile(cert_file):
        os.environ["REQUESTS_CA_BUNDLE"] = cert_file

def get(url, token, endpoint, sanitize=True):
    """Perform a GET request with the 'urllib2' library.

    Args:
      url (str): The base URL to get from.
      token (str): The vault token for authentication.
      endpoint (str): The API endpoint to get.
      sanitize (boolean): Whether or not we should attempt to sanitize the
        given URL, defaults to True.

    Returns:
      Response data

    """
    if sanitize:
        url = sanitize_url(url)
    logger.debug("Getting %s%s" % (url, endpoint))
    opener = urllib2.build_opener()
    opener.addheaders.append(('Cookie', 'token=' + token))
    f = opener.open(url + endpoint)
    contents = f.read()

    data = json.loads(contents)
    return data


def r_get(url, token, endpoint, sanitize=True):
    """Perform a GET request with the 'requests' library.

    Args:
      url (str): The base URL to get from.
      token (str): The vault token for authentication.
      endpoint (str): The API endpoint to get.
      sanitize (boolean): Whether or not we should attempt to sanitize the
        given URL, defaults to True.

    Returns:
      Response data

    """
    if sanitize:
        url = sanitize_url(url)
    logger.debug("Getting '%s%s'" % (url, endpoint))
    r = requests.get(url + endpoint, cookies={"token": token})

    if r.text:
        data = json.loads(r.text)
    else:
        data = ""
    return data


def put(url, token, path, data, sanitize=True):
    """Perform a PUT request with the 'requests' library.

    Args:
      url (str): The base URL to put to.
      token (str): The vault token for authentication.
      path (str): The API endpoint to hit.
      data (dict): A dictionary of data to put.
      sanitize (boolean): Whether or not we should attempt to sanitize the
        given URL, defaults to True.

    Returns:
      Response data

    """
    if sanitize:
        url = sanitize_url(url)
    logger.debug("Putting '%s%s'" % (url, path))
    r = requests.put(url + path, data=json.dumps(data), cookies={"token": token})

    if r.text:
        data = json.loads(r.text)
    else:
        data = ""
    return data


def delete(url, token, path, sanitize=True):
    """Perform a DELETE request with the 'requests' library.

    Args:
      url (str): The base URL to delete from.
      token (str): The vault token for authentication.
      path (str): The API endpoint to delete.
      sanitize (boolean): Whether or not we should attempt to sanitize the
        given URL, defaults to True.

    Returns:
      Response data

    """
    if sanitize:
        url = sanitize_url(url)
    logger.debug("Deleting '%s%s'" % (url, path))
    r = requests.delete(url + path, cookies={"token": token})

    if r.text:
        data = json.loads(r.text)
    else:
        data = ""
    return data


def sanitize_url(url):
    """Ensures that the URL ends with a '/' and has the API version in it.

    Args:
      url (str): The URL to sanitize.

    Returns:
      The sanitized URL string.

    """
    url = str(url)
    logger.debug("Sanitizing URL: '%s'" % url)
    if not url.endswith('/'):
        url += '/'
    if not url.endswith('v1/'):
        url += 'v1/'

    return url


def get_mounts(url, token):
    """Gets all available mounts from vault server.

    Args:
      url (str): The base vault URL to get from.
      token (str): The vault token for authentication

    Returns:
      Response data

    """
    endpoint = '/sys/mounts'
    logger.debug("Fetching available mounts from '%s%s'" % (str(url), endpoint))
    contents = get(url, token, endpoint)
    return contents


def get_listings(url):
    """Gets a listing of all available secrets from VaultDiscover.

    Args:
      url (str): The VaultDiscover URL to fetch from.

    Returns:
      Response data with available secrets.

    """
    logger.debug("Fetching list of secrets from '%s'" % str(url))
    response = urllib2.urlopen(str(url))
    contents = response.read()
    data = json.loads(contents)

    return data


def write_secret(url, token, path, data):
    """Writes a secret to the Vault server.

    Args:
      url (str): The base vault URL to write the secret to.
      token (str): The vault token for authentication.
      path (str): The path to write the secret to, e.g. /secret/foo
      data (dict): A dictionary of key/values to write.

    Returns:
      Response data

    """
    url = sanitize_url(url)
    logger.debug("Writing secret to '%s%s'" % (url, path))
    data = put(url, token, path, data)

    return data


def delete_secret(url, token, path):
    """Deletes a secret from the Vault server.

    Args:
      url (str): The base vault URL.
      token (str): The vault token for authentication.
      path (str): The path to the secret to delete, e.g. /secret/foo

    Returns:
      Response data

    """
    url = sanitize_url(url)
    logger.debug("Deleting secret at '%s%s'" % (url, path))
    data = delete(url, token, path)

    return data


def read_secret(url, token, path):
    """Reads a secret from the Vault server.

    Args:
      url (str): The base vault URL.
      token (str): The vault token for authentication.
      path (str): The path to the secret to read, e.g. /secret/foo

    Returns:
      Response data

    """
    url = sanitize_url(url)
    logger.debug("Reading secret from '%s%s'" % (url, path))
    data = r_get(url, token, path)

    return data


def lookup_self(url, token):
    """Looks up the current token's details.

    Args:
      url (str): The base vault URL.
      token (str): The vault token for authentication.

    Returns:
      Response data

    """
    endpoint = '/auth/token/lookup-self'
    logger.debug("Looking up token: '%s%s'" % (url, endpoint))
    contents = get(url, token, endpoint)
    return contents


def seal_status(url, token):
    """Gets the Vault's current seal status.

    Args:
      url (str): The base vault URL.
      token (str): The vault token for authentication.

    Returns:
      Response data

    """
    endpoint = '/sys/seal-status'
    logger.debug("Getting seal status: '%s%s'" % (url, endpoint))
    contents = get(url, token, endpoint)


def seal_vault(url, token):
    """Seals the Vault.

    Args:
      url (str): The base vault URL.
      token (str): The vault token for authentication.

    Returns:
      Response data

    """
    endpoint = '/sys/seal'
    logger.debug("Sealing the vault: '%s%s'" % (url, endpoint))
    contents = put(url, token, path, {})


def unseal_vault(url, token, key):
    pass


if __name__ == "__main__":
    print get_mounts("http://127.0.0.1:8200/v1/", "0d366ace-b059-dbd4-30ce-6f9dbc763294")
    print lookup_self("http://127.0.0.1:8200/v1/", "0d366ace-b059-dbd4-30ce-6f9dbc763294")
    print write_secret("http://127.0.0.1:8200/v1/", "0d366ace-b059-dbd4-30ce-6f9dbc763294", "secret/ididnt/exist/before", {"value": "test"})
    print read_secret("http://127.0.0.1:8200/v1/", "0d366ace-b059-dbd4-30ce-6f9dbc763294", "secret/ididnt/exist/before")
