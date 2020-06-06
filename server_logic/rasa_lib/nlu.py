from collections import namedtuple
from translation import Translator
from aiohttp import ClientSession
from settings import RASA_URL, ROOT_PATH
from typing import Optional, Union, List
from . import Language
import asyncio
import logging
import iso639
import json


Entity = namedtuple("Entity", ["value", "entity"])
with open(ROOT_PATH / "rasa" / "pure_nlu" / "csv" / "raw_data" / "country_languages.json") as file_:
    available_langs = json.load(file_)


class NLUWorker:
    GET_ENTITIES_URL = f"{RASA_URL}/model/parse"

    def __init__(self, translation_api: Translator):
        self.tr = translation_api

    async def _detect_entities(self, text: str, http: ClientSession):
        async with http.post(self.GET_ENTITIES_URL, json={"text": text}) as resp:
            data = await resp.json()
            for each_entity in data['entities']:
                yield Entity(value=each_entity['value'], entity=each_entity['entity'])

    async def detect_language(self, text: str) -> Optional[Union[Language, List[Language]]]:
        async with ClientSession() as http:
            # 1) Try to detect entity using rasa nlu
            async for each_entity in self._detect_entities(text, http):
                if each_entity.entity in ['language', 'country', 'country_flag']:
                    raw_language_obj = iso639.find(each_entity.value)
                    # False positive from rasa (maybe add some strings comparison later
                    if raw_language_obj and raw_language_obj['name'] != "Undetermined":
                        logging.info(f"NLU model detected language: ({text})[{raw_language_obj['name']}]")
                        return raw_language_obj
                if each_entity.entity in ['country', 'country_flag']:
                    # Returned country name
                    # Our dict must have mapping to the country
                    langs = available_langs.get(each_entity.value)
                    if langs:
                        logging.info(f"NLU model detected country: ({text})[{each_entity.entity}]")
                        langs = [iso639.find(lang) for lang in langs]
                        return [lang_obj for lang_obj in langs if lang_obj and lang_obj['name'] != "Undetermined"]
            else:
                # 2) Detect what is the language of the speaker
                language = await self.tr.detect_language(text, http)
                logging.info(f"Translator detected language: ({text})[{language}]")
                # If user sent message in his own language and we figured out what is it - case closed
                language = iso639.find(language)
                if language and language['name'] != "Undetermined":
                   return language 
