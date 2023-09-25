import gettext
import os

PACKAGE_DIR = os.path.dirname(__file__)
LOCALE_DIR = os.path.join(PACKAGE_DIR, "locales")


class Translation:
    def __init__(self):
        self._languages = {}

    def initialize_translation(self, language):
        translation = gettext.translation("messages", LOCALE_DIR, [language], fallback=True)
        self._languages[language] = translation
        return translation

    def translate(self, msgid, language):
        translation = self._languages.get(language)
        if translation is None:
            translation = self.initialize_translation(language)
        return translation.gettext(msgid)


translation = Translation()

translate = translation.translate


def _(msgid):
    """A simple function to mark up a text to translate.

    This doesn't do the translation but if you use it will show up in the
    message catalog.
    """
    return msgid
