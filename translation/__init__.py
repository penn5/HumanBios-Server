from settings import CLOUD_TRANSLATION_API_KEY
from aiohttp import ClientSession
import logging
import asyncio
import ujson


class Translator:
    TRANSLATION_URL = f"https://translation.googleapis.com/language/translate/v2?key={CLOUD_TRANSLATION_API_KEY}"
    DETECTION_URL = f"https://translation.googleapis.com/language/translate/v2/detect?key={CLOUD_TRANSLATION_API_KEY}"
    HEADERS = {
        "Content-Type": "application/json; charset=utf-8",
    }

    # @Thought: Maybe drop __init__ func and move key to the class var
    # @Thought: then change all methods to @classmethod
    def __init__(self):
        self.key = CLOUD_TRANSLATION_API_KEY

    async def __get_json(self, url: str, data: dict, headers: dict, session: ClientSession):
        if session:
            async with session.post(url, json=data, headers=headers) as response:
                return await response.json()
        else:
            async with ClientSession() as session:
                async with session.post(url, json=data, headers=headers) as response:
                    return await response.json()

    async def detect_language(self,
                              text: str,
                              session: ClientSession = None):
        data = {
            'q': text
        }
        result = await self.__get_json(self.DETECTION_URL, data, self.HEADERS, session)
        # Schema: [[{LANG}], ...], where LANG: {"language": "en"}
        # logging.info(result)
        return result['data']['detections'][0][0]["language"]

    async def translate_text(self,
                             text: str,
                             target: str,
                             session: ClientSession = None,
                             from_lang: str = 'en'):
        data = {
            'source': from_lang,
            'target': target,
            'format': 'text',
            'q': text
        }
        result = await self.__get_json(self.TRANSLATION_URL, data, self.HEADERS, session)
        logging.info(result)
        return result['data']['translations'][0]['translatedText']

    async def translate_dict(self, target: str, texts: dict, from_lang: str = 'en'):
        new_texts = dict()
        async with ClientSession() as session:
            for key, each_text in texts.items():
                new_text: str = await self.translate_text(each_text, target, session)
                #:< Hacks
                new_text = new_text.replace("& deg;", "°")
                #
                new_texts[key] = new_text
        return new_texts

    async def translate_multiple_languages_dict(self, languages: list, source_dict: dict, from_lang: str = 'en'):
        tasks_group = asyncio.gather(*[self.translate_dict(language, source_dict, from_lang) for language in languages])
        results = await tasks_group
        # [DEBUG]:
        # print(f"Source: {source_dict}")
        # print(*results, sep='\n')
        return results

    async def translation(self, source_file: str, from_lang: str, languages: list, output_file: str):
        with open(source_file) as source:
            source = ujson.load(source)

        results = await self.translate_multiple_languages_dict(languages, source, from_lang)
        result_json = dict()
        languages = [from_lang] + languages
        results = [source] + list(results)

        for key, result in zip(languages, results):
            result_json[key] = result

        with open(output_file, "w") as output:
            ujson.dump(result_json, output, indent=4)

        print("Translation done!")
