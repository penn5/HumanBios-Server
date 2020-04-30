from . import Translator


if __name__ == "__main__":
    tr = Translator()
    # [DEBUG]:
    # asyncio.get_event_loop().run_until_complete(
    #     tr.translate_multiple_languages_dict(
    #         ['de', 'ru', 'es', 'fr', 'uk'],
    #         {
    #          "question_P": "Hey, Poo, did you know that asyncio is superior?",
    #          "P_answer_1": "Yes, I knew",
    #          "P_answer_2": "Of course, I knew!"
    #         },
    #         'en')
    # )