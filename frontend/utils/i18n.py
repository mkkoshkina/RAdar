import json
import os
import logging

# Set up logging
logger = logging.getLogger(__name__)

I18N_PATH = os.path.join(os.path.dirname(__file__), '../assets/i18n')

LANG_FILES = {
    'en': 'en.json',
    'ru': 'ru.json',
}

# Cache for translations to avoid repeated file reads
_translation_cache = {}

def load_translations(lang: str = 'en'):
    """Load translations with caching and error handling"""
    if lang in _translation_cache:
        return _translation_cache[lang]
    
    file = LANG_FILES.get(lang, 'en.json')
    path = os.path.join(I18N_PATH, file)
    
    try:
        with open(path, encoding='utf-8') as f:
            translations = json.load(f)
            _translation_cache[lang] = translations
            return translations
    except FileNotFoundError:
        logger.error(f"Translation file not found: {path}")
        # Fallback to English if available
        if lang != 'en':
            return load_translations('en')
        return {}
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in translation file: {path}")
        if lang != 'en':
            return load_translations('en')
        return {}
    except Exception as e:
        logger.error(f"Error loading translations for {lang}: {e}")
        return {}

def t(key: str, lang: str = 'en', fallback: str = None):
    """Get translation with fallback support"""
    translations = load_translations(lang)
    
    # Try to get translation in requested language
    if key in translations:
        return translations[key]
    
    # Try English fallback if not the original language
    if lang != 'en':
        english_translations = load_translations('en')
        if key in english_translations:
            logger.warning(f"Translation missing for key '{key}' in {lang}, using English fallback")
            return english_translations[key]
    
    # Use provided fallback or return the key itself
    if fallback:
        return fallback
    
    logger.warning(f"Translation missing for key '{key}' in language '{lang}'")
    return key

def get_supported_languages():
    """Return list of supported language codes"""
    return list(LANG_FILES.keys())

def clear_translation_cache():
    """Clear the translation cache (useful for testing or dynamic reloading)"""
    global _translation_cache
    _translation_cache = {}