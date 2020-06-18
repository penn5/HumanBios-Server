from settings import ROOT_PATH, STATIC_URL
import logging
import json
import os


with open(os.path.join(ROOT_PATH, "files", "files.json")) as filenames:
    FILENAMES =  json.load(filenames)

for key, paths in FILENAMES.items():
    FILENAMES[key] = [f"{STATIC_URL}/{path}" for path in paths]

logging.info(f"Loaded files: {FILENAMES}")
