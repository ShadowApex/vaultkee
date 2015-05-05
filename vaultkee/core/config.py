#!/usr/bin/python

import os
from ConfigParser import ConfigParser
from os.path import expanduser

home = expanduser("~")
config_dir = home + "/.vaultkee"
config_file = config_dir + "/settings.conf"


def generate_config():
    config = ConfigParser()
    os.makedirs(config_dir)
    f = open(config_file, 'w')
    config.add_section('VaultKee')
    config.set('VaultKee', 'url', 'http://127.0.0.1:8200')
    config.set('VaultKee', 'listing_url', 'http://127.0.0.1:5000/')
    config.set('VaultKee', 'token', '')
    config.set('VaultKee', 'save', True)
    config.write(f)
    f.close()


def load_config():
    config = ConfigParser()
    if not os.path.isdir(config_dir):
        generate_config()
    config.read(config_file)

    return config


def save_config(url, listing_url, token, save):
    config = ConfigParser()
    f = open(config_file, 'w')
    config.add_section('VaultKee')
    config.set('VaultKee', 'url', url)
    config.set('VaultKee', 'listing_url', listing_url)
    config.set('VaultKee', 'token', token)
    config.set('VaultKee', 'save', save)
    config.write(f)
    f.close()


if __name__ == "__main__":
    load_config()
    save_config("http://127.0.0.1:8200",
                "http://127.0.0.1:5000",
                "ea75ca7f-0b8f-d618-83e7-6cfac18de178",
                True)
