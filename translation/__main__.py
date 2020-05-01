from . import Translator
import argparse
import asyncio


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="translation", description='Translate file into multiple languages.')
    parser.add_argument('file_input', type=str, help='input file to translate from')
    parser.add_argument('language_input', type=str, help='language to translate from')
    parser.add_argument('languages_output', type=str, nargs='+', help='languages to translate input file to')
    parser.add_argument('output_file', type=str, help='output file for the translations')

    args = parser.parse_args()
    tr = Translator()

    asyncio.get_event_loop().run_until_complete(
        tr.translation(
            args.file_input,
            args.language_input,
            args.languages_output,
            args.output_file
        )
    )
    # [EXAMPLE]: python -m translation strings.json en de ru es fr uk all_strings.json