#!/usr/bin/python
import json
import os
from flask import Flask
from ConfigParser import ConfigParser
app = Flask(__name__)

config = ConfigParser()
config.read("settings.conf")
LOGICAL_DIR = config.get("VaultKeeLs", "logical_path")

def explore(rootdir):
    """
    Creates a nested dictionary that represents the folder structure of rootdir
    """
    dir = {}
    rootdir = rootdir.rstrip(os.sep)
    start = rootdir.rfind(os.sep) + 1
    for path, dirs, files in os.walk(rootdir):
        folders = path[start:].split(os.sep)
        subdir = dict.fromkeys(files)
        parent = reduce(dict.get, folders[:-1], dir)
        parent[folders[-1]] = subdir

    for key, value in dir.items():
        for k, v in value.items():
            return v

@app.route('/v1')
def list_vault():
    return json.dumps(explore(LOGICAL_DIR))

@app.route('/')
def list_index():
    return json.dumps(explore(LOGICAL_DIR))

if __name__ == '__main__':
    app.run()
