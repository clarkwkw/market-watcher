from .message_id import MessageID
from .language import Language
from .language_text import LANGUAGES


class Translator:
    def translate(
        self,
        message_id: MessageID,
        language: Language = Language.EN,
        **kwargs
    ):
        template_str = LANGUAGES[language].get(message_id, f"<{message_id}>")
        return template_str.format(**kwargs)
