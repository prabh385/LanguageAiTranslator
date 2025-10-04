import logging
import time
from googletrans import Translator

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def translate_text(text, target_lang='hi'):
    """
    Pure Google Translate integration - translates any text with robust error handling
    """
    max_retries = 3
    retry_delay = 2  # seconds
    
    for attempt in range(max_retries):
        try:
            logger.info(f"🔄 Translating to {target_lang} (attempt {attempt + 1}/{max_retries}): '{text}'")
            
            # Validate input
            if not text or not text.strip():
                logger.warning("Empty text provided for translation")
                return ""
            
            text = text.strip()
            
            # Map language codes to Google Translate codes
            lang_map = {
                'hi': 'hi',  # Hindi
                'ta': 'ta',  # Tamil
                'te': 'te',  # Telugu
                'ml': 'ml',  # Malayalam
                'bn': 'bn',  # Bengali
                'mr': 'mr',  # Marathi
                'gu': 'gu',  # Gujarati
                'kn': 'kn',  # Kannada
                'pa': 'pa'   # Punjabi
            }
            
            google_lang = lang_map.get(target_lang, 'hi')
            logger.debug(f"Using Google language code: {google_lang}")
            
            # Create new translator instance for each request (avoids connection issues)
            translator = Translator()
            
            # Set timeout and perform translation
            translated = translator.translate(
                text, 
                dest=google_lang,
                timeout=10
            )
            
            if translated and hasattr(translated, 'text') and translated.text:
                translated_text = translated.text.strip()
                
                # Validate translation quality
                if translated_text and translated_text.lower() != text.lower():
                    logger.info(f"✅ Translation successful: '{translated_text}'")
                    return translated_text
                else:
                    logger.warning(f"⚠️ Translation returned same text: '{translated_text}'")
                    if attempt == max_retries - 1:
                        return get_emergency_fallback(text, target_lang)
            else:
                logger.error("❌ Translation returned empty or invalid result")
                if attempt == max_retries - 1:
                    return get_emergency_fallback(text, target_lang)
                    
        except Exception as e:
            error_msg = str(e)
            logger.error(f"❌ Translation attempt {attempt + 1} failed: {error_msg}")
            
            # Handle specific common errors
            if "timed out" in error_msg.lower():
                logger.warning("⏰ Translation timeout, retrying...")
            elif "connection" in error_msg.lower():
                logger.warning("🌐 Connection issue, retrying...")
            elif "service" in error_msg.lower():
                logger.warning("🔧 Service unavailable, retrying...")
            else:
                logger.warning(f"🔄 Unknown error, retrying...: {error_msg}")
            
            # Final attempt - return emergency fallback
            if attempt == max_retries - 1:
                logger.error(f"💥 All translation attempts failed for: '{text}'")
                return get_emergency_fallback(text, target_lang)
            
            # Wait before retry with exponential backoff
            sleep_time = retry_delay * (attempt + 1)
            logger.info(f"⏳ Waiting {sleep_time}s before retry...")
            time.sleep(sleep_time)
    
    # This should never be reached, but just in case
    return get_emergency_fallback(text, target_lang)

def get_emergency_fallback(text, target_lang):
    """
    Emergency fallback when all translation attempts fail
    Returns a basic formatted response
    """
    logger.warning(f"🚨 Using emergency fallback for: '{text}' -> {target_lang}")
    
    lang_names = {
        'hi': 'Hindi', 'ta': 'Tamil', 'te': 'Telugu', 'ml': 'Malayalam',
        'bn': 'Bengali', 'mr': 'Marathi', 'gu': 'Gujarati', 'kn': 'Kannada', 'pa': 'Punjabi'
    }
    
    lang_name = lang_names.get(target_lang, 'Unknown')
    
    # Return a clear indication that translation failed
    return f"[{lang_name} Translation] {text}"

def batch_translate(texts, target_lang='hi'):
    """
    Translate multiple texts at once (more efficient for batches)
    """
    try:
        if not texts:
            return []
        
        if isinstance(texts, str):
            texts = [texts]
        
        logger.info(f"📦 Batch translating {len(texts)} texts to {target_lang}")
        
        # Map language codes
        lang_map = {
            'hi': 'hi', 'ta': 'ta', 'te': 'te', 'ml': 'ml', 'bn': 'bn',
            'mr': 'mr', 'gu': 'gu', 'kn': 'kn', 'pa': 'pa'
        }
        
        google_lang = lang_map.get(target_lang, 'hi')
        translator = Translator()
        
        # Translate all texts at once
        translations = translator.translate(texts, dest=google_lang)
        
        results = []
        for i, translation in enumerate(translations):
            if translation and translation.text:
                results.append(translation.text)
                logger.debug(f"Batch item {i+1}: '{texts[i]}' -> '{translation.text}'")
            else:
                logger.warning(f"Batch item {i+1} failed, using fallback")
                results.append(get_emergency_fallback(texts[i], target_lang))
        
        logger.info(f"✅ Batch translation completed: {len(results)} texts")
        return results
        
    except Exception as e:
        logger.error(f"❌ Batch translation failed: {str(e)}")
        # Fallback to individual translations
        return [translate_text(text, target_lang) for text in texts]

def get_supported_languages():
    """
    Get list of supported languages and their codes
    """
    supported_langs = {
        'hi': {'code': 'hi', 'name': 'Hindi', 'native_name': 'हिन्दी'},
        'ta': {'code': 'ta', 'name': 'Tamil', 'native_name': 'தமிழ்'},
        'te': {'code': 'te', 'name': 'Telugu', 'native_name': 'తెలుగు'},
        'ml': {'code': 'ml', 'name': 'Malayalam', 'native_name': 'മലയാളം'},
        'bn': {'code': 'bn', 'name': 'Bengali', 'native_name': 'বাংলা'},
        'mr': {'code': 'mr', 'name': 'Marathi', 'native_name': 'मराठी'},
        'gu': {'code': 'gu', 'name': 'Gujarati', 'native_name': 'ગુજરાતી'},
        'kn': {'code': 'kn', 'name': 'Kannada', 'native_name': 'ಕನ್ನಡ'},
        'pa': {'code': 'pa', 'name': 'Punjabi', 'native_name': 'ਪੰਜਾਬੀ'}
    }
    
    return supported_langs

def test_translation():
    """
    Test function to verify translation is working
    """
    test_cases = [
        ("hello", "hi"),
        ("how are you", "ta"),
        ("thank you", "te"),
        ("good morning", "ml"),
        ("what is your name", "bn")
    ]
    
    print("🧪 Testing Google Translate Integration...")
    print("=" * 50)
    
    for text, lang in test_cases:
        try:
            result = translate_text(text, lang)
            print(f"✅ '{text}' -> {lang}: '{result}'")
        except Exception as e:
            print(f"❌ '{text}' -> {lang}: FAILED - {e}")
    
    print("=" * 50)
    print("🎯 Test completed!")

# Keep backward compatibility
def translate_text_old(text, target_lang='hi'):
    return translate_text(text, target_lang)

# Run test if file is executed directly
if __name__ == '__main__':
    test_translation()