import click
from google.cloud import translate_v2 as translate
import os

# Loads the credentials from the credentials.json file into the GOOGLE_APPLICATION_CREDENTIALS environment variable.
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'credentials.json'


@click.command()
@click.argument('text')
@click.option('--target', '-t', default='es', help='Target language to translate the text')
def translate_cmd(text, target_lang='es'):
    """
    This function uses the Google Cloud Translate API to translate a given text to a target language.
    :param text: The source text to translate. This is mandatory.
    :param target_lang: The target language to translate the text. This is optional and defaults to 'es' (Spanish).
    """

    # Creates a new API client to interact with GCP Translate API.
    # This will use the credentials loaded in the GOOGLE_APPLICATION_CREDENTIALS environment variable.
    translate_client = translate.Client()

    # Uses Translate API to detect the language of the input text.
    # The result is an object containing the original input text, the detected language code and confidence score.
    detect_lang_res = translate_client.detect_language(text)

    # Display a user-friendly message with the detected language and confidence score.
    print(f"Lenguaje detectado: '{detect_lang_res['language']}' [confianza: {detect_lang_res['confidence']:0.2%}]")

    # Uses the Translate API to translate the input text to the target language (spanish by default).
    # The result is an object containing the original input text, the translated text and the detected source language.
    # The detected source language is the same as the one detected in the previous step.
    translation_res = translate_client.translate(text, target_language=target_lang)

    # Display a user-friendly message with the translated text.
    print(f"Traducción a '{target_lang}': {translation_res['translatedText']}")


if __name__ == '__main__':
    translate_cmd()
