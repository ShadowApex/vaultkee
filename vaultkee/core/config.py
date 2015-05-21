#!/usr/bin/python

import os
import logging
import json
from ConfigParser import ConfigParser
from os.path import expanduser

home = expanduser("~")
config_dir = home + "/.vaultkee"
config_file = config_dir + "/settings.conf"
cache_file = config_dir + "/cache.json"

# Set up logging
logger = logging.getLogger(__name__)

def generate_config():
    logger.debug("Generating default configuration")
    config = ConfigParser()
    if not os.path.isdir(config_dir):
        os.makedirs(config_dir)
    f = open(config_file, 'w')
    config.add_section('VaultKee')
    config.set('VaultKee', 'url', '0')
    config.set('VaultKee', 'listing_url', '0')
    config.set('VaultKee', 'save', True)
    config.write(f)
    f.close()


def generate_cache():
    logger.debug("Generating empty cache of server URLs")
    if not os.path.isdir(config_dir):
        os.makedirs(config_dir)
    f = open(cache_file, "w")
    cache = {"vaults": ["http://127.0.0.1:8200"],
             "listings": ["http://127.0.0.1:5000/"]}
    json.dump(cache, f)
    f.close()


def load_config():
    logger.debug("Loading existing config file")
    config = ConfigParser()
    if not os.path.isfile(config_file):
        generate_config()
    config.read(config_file)

    return config


def load_cache():
    logger.debug("Loading URLs from cache")
    if not os.path.isfile(cache_file):
        generate_cache()
    f = open(cache_file, "r")
    cache = json.load(f)
    f.close()

    return cache


def save_config(url, listing_url, save):
    logger.debug("Saving configuration")
    config = ConfigParser()
    f = open(config_file, 'w')
    config.add_section('VaultKee')
    config.set('VaultKee', 'url', url)
    config.set('VaultKee', 'listing_url', listing_url)
    config.set('VaultKee', 'save', save)
    config.write(f)
    f.close()


def save_cache(vaults, listings, append=False):
    logger.debug("Saving vaults and listings to cache")

    if append:
        logger.debug("Appending vaults and listings to the current cache")
        cache = load_cache()
    else:
        logger.debug("Overwriting existing cache")
        cache = {'vaults': [], 'listings': []}

    cache['vaults'] += vaults
    cache['listings'] += listings

    # Remove any duplicates by converting our list to a set then back
    # to a list.
    new_vaults = list(set(cache['vaults']))
    new_listings = list(set(cache['listings']))
    cache['vaults'] = new_vaults
    cache['listings'] = new_listings

    f = open(cache_file, 'w')
    json.dump(cache, f)
    f.close()


if __name__ == "__main__":
    load_config()
    save_config("http://127.0.0.1:8200",
                "http://127.0.0.1:5000",
                True)
