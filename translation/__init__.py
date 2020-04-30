from settings import CLOUD_TRANSLATION_API_KEY
from aiohttp import ClientSession
import asyncio


class Translator:
    URL = f"https://translation.googleapis.com/language/translate/v2?key={CLOUD_TRANSLATION_API_KEY}"
    HEADERS = {
        "Content-Type": "application/json",
    }

    def __init__(self):
        self.key = CLOUD_TRANSLATION_API_KEY

    async def translate_text(self,
                             target: str,
                             text: str,
                             session: ClientSession = None,
                             from_lang: str = 'en'):
        data = {
            'source': from_lang,
            'target': target,
            'format': 'text',
            'q': text
        }
        if session:
            async with session.post(self.URL, json=data, headers=self.HEADERS) as response:
                result = await response.json()
        else:
            async with ClientSession() as session:
                async with session.post(self.URL, json=data, headers=self.HEADERS) as response:
                    result = await response.json()
        return result['data']['translations'][0]['translatedText']

    async def translate_dict(self, target: str, texts: dict, from_lang: str = 'en'):
        new_texts = dict()
        async with ClientSession() as session:
            for key, each_text in texts.items():
                new_text = await self.translate_text(target, each_text, session)
                new_texts[key] = new_text
        return new_texts

    async def translate_multiple_languages_dict(self, languages: list, source_dict: dict, from_lang: str = 'en'):
        tasks_group = asyncio.gather(*[self.translate_dict(language, source_dict, ) for language in languages])
        results = await tasks_group
        # [DEBUG]:
        # print(f"Source: {source_dict}")
        # print(*results, sep='\n')
        return results