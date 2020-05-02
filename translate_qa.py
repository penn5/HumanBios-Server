from strings.qa_module.methods import get_english_strings, put_translated_strings
from translation import Translator
import asyncio


async def main(languages: list):
    tr = Translator()
    english = get_english_strings()
    results = await tr.translate_multiple_languages_dict(languages, english)
    for language, translation in zip(languages, results):
        put_translated_strings(language, translation)


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main(['ru', 'uk', 'es', 'fr']))