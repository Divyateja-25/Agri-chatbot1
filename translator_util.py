from deep_translator import GoogleTranslator

# We have removed the problematic import from 'deep_translator.detection'

def translate_text(text, dest="en"):
    """Translates text to a destination language."""
    try:
        translated_text = GoogleTranslator(source='auto', target=dest).translate(text)
        return translated_text
    except Exception as e:
        print(f"Translation error: {e}")
        return text

def detect_language(text):
    """
    Detects the language of a given text using a new, more stable method.
    """
    try:
        # This new method creates a translator object first
        # and then uses its built-in .detect() method.
        detected_result = GoogleTranslator().detect(text)
        
        # The result is a list like ['en', 'english'], so we take the first item.
        lang_code = detected_result[0]
        return lang_code
    except Exception as e:
        print(f"Language detection error: {e}")
        return "en"

