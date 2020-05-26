from collections import namedtuple
from translation import Translator
from aiohttp import ClientSession
from settings import RASA_URL
from typing import Optional
from . import Language
import logging
import iso639


Entity = namedtuple("Entity", ["value", "entity"])


class NLUWorker:
    GET_ENTITIES_URL = f"{RASA_URL}/model/parse"

    def __init__(self, translation_api: Translator):
        self.http = ClientSession()
        self.tr = translation_api

    async def _detect_entities(self, text: str):
        async with self.http as http:
            async with http.post(self.GET_ENTITIES_URL, json={"text": text}) as resp:
                data = await resp.json()
                for each_entity in data['entities']:
                    yield Entity(value=each_entity['value'], entity=each_entity['entity'])

    async def detect_language(self, text: str) -> Optional[Language]:
        # 1) Detect what is the language of the speaker
        language = await self.tr.detect_language(text, self.http)
        # If user sent message in his own language and we figured out what is it - case closed
        if language != "en":
            logging.info(f"Translator detected language: ({text})[{language}]")
            return iso639.find(language)
        # 2) Try to detect entity using rasa nlu
        async for each_entity in self._detect_entities(text):
            if each_entity.entity in ['language_code', 'language_name']:
                raw_language_obj = iso639.find(each_entity.value)
                logging.info(f"NLU model detected language: ({text})[{raw_language_obj['name']}]")
                return raw_language_obj
        else:
            # Will return None if not detected any
            return