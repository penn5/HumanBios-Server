from settings import ROOT_PATH
import json
import os


with open(os.path.join(ROOT_PATH, "files", "files.json")) as filenames:
    FILENAMES = json.load(filenames)