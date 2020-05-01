from settings import ROOT_PATH
import json
import os


def load(*path):
    path = os.path.join(ROOT_PATH, *path)
    with open(path) as strings:
        return json.load(strings)


strings_text = load('strings', 'json', 'all_strings.json')