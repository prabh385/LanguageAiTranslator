import logging
from googletrans import Translator
import time
import re

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize the translator with retry mechanism
def get_translator():
    max_retries = 3
    retry_delay = 1  # seconds
    
    for attempt in range(max_retries):
        try:
            return Translator()
        except Exception as e:
            if attempt < max_retries - 1:
                logger.warning(f"Failed to initialize translator (attempt {attempt + 1}/{max_retries}): {str(e)}")
                time.sleep(retry_delay)
            else:
                logger.error(f"Failed to initialize translator after {max_retries} attempts: {str(e)}")
                raise

def translate_text(text, target_lang='hi'):
    """
    Translate text to the target language using Google Translate.
    Creates a new translator instance for each request to avoid rate limiting.
    """
    try:
        logger.debug(f"Translating text to {target_lang}")
        
        if not text or not text.strip():
            logger.warning("Empty text provided for translation")
            return ""
            
        # Create a new translator instance for each request
        translator = Translator()
        
        # Map language codes to Google Translate codes
        lang_map = {
            'hi': 'hi',  # Hindi
            'ta': 'ta',  # Tamil
            'te': 'te',  # Telugu
            'ml': 'ml',  # Malayalam
            'bn': 'bn'   # Bengali
        }
        
        # Get the Google Translate language code
        google_lang = lang_map.get(target_lang, 'hi')
        
        # Perform the translation
        result = translator.translate(text, dest=google_lang)
        translated_text = result.text
        
        logger.debug(f"Translation successful: {translated_text[:100]}...")
        return translated_text
        
    except Exception as e:
        logger.error(f"Translation error: {str(e)}")
        # Return original text if translation fails
        return text

def translate_text_old(text, target_lang='hi'):
    """
    Translate the input text from English to the target language.
    
    Args:
        text (str): Text to translate
        target_lang (str): Target language code (hi, ta, te, ml, bn)
        
    Returns:
        str: Translated text
    """
    logger.info(f"Translating text to {target_lang}: {text}")
    
    # For demo purposes, we'll use a simplified approach with some 
    # predefined translations and patterns instead of a real translation API
    
    # Preserve proper nouns (anything that starts with a capital letter after space)
    # We'll use a regex to find them and protect them during translation
    
    # Step 1: Identify and protect proper nouns
    proper_nouns = []
    
    # Improved pattern to better match "My name is NAME" constructs
    name_pattern = r'([Mm]y name is|[Mm]y name\'s|[Ii] am|[Ii]\'m|[Cc]all me|[Nn]amed) ([A-Z][a-z]+)'
    name_matches = re.finditer(name_pattern, text)
    
    for match in name_matches:
        name = match.group(2)  # The actual name
        if name not in proper_nouns:
            proper_nouns.append(name)

    # More general pattern for proper nouns
    general_pattern = r'\b([A-Z][a-z]+)\b'
    general_matches = re.finditer(general_pattern, text)
    
    for match in general_matches:
        name = match.group(1)
        # Exclude common English words that start with capital letters
        common_words = ['I', 'A', 'The', 'This', 'That', 'These', 'Those', 'My', 'Your', 'His', 'Her']
        if name not in common_words and name not in proper_nouns:
            proper_nouns.append(name)
    
    # Step 2: Replace proper nouns with placeholders
    placeholder_text = text
    for i, name in enumerate(proper_nouns):
        placeholder_text = placeholder_text.replace(name, f"__PROPER_NOUN_{i}__")
    
    # Step 3: Simplified translation
    # In a real implementation, this would call a translation API
    translated_text = ""
    
    # Hindi translations (could be extended to other languages)
    if target_lang == 'hi':
        # Split text into sentences and translate each one
        sentences = re.split(r'([.!?])', placeholder_text)
        for i in range(0, len(sentences), 2):
            sentence = sentences[i].strip()
            if not sentence:
                continue
                
            punctuation = sentences[i+1] if i+1 < len(sentences) else ""
            
            # Simple phrase translations
            if re.match(r'hello|hi|hey', sentence, re.IGNORECASE):
                translated_text += "नमस्ते" + punctuation + " "
            elif re.match(r'how are you', sentence, re.IGNORECASE):
                translated_text += "आप कैसे हैं" + punctuation + " "
            elif re.match(r'my name is __PROPER_NOUN_\d+__', sentence, re.IGNORECASE):
                # Special handling for "my name is" pattern
                name_idx = int(re.search(r'__PROPER_NOUN_(\d+)__', sentence).group(1))
                translated_text += f"मेरा नाम {proper_nouns[name_idx]} है" + punctuation + " "
            elif re.match(r'i am __PROPER_NOUN_\d+__', sentence, re.IGNORECASE):
                # Special handling for "I am" pattern
                name_idx = int(re.search(r'__PROPER_NOUN_(\d+)__', sentence).group(1))
                translated_text += f"मैं {proper_nouns[name_idx]} हूं" + punctuation + " "
            elif re.match(r'nice to meet you', sentence, re.IGNORECASE):
                translated_text += "आपसे मिलकर अच्छा लगा" + punctuation + " "
            elif re.match(r'thank you', sentence, re.IGNORECASE):
                translated_text += "धन्यवाद" + punctuation + " "
            elif re.match(r'you\'re welcome', sentence, re.IGNORECASE):
                translated_text += "आपका स्वागत है" + punctuation + " "
            elif re.match(r'good morning', sentence, re.IGNORECASE):
                translated_text += "सुप्रभात" + punctuation + " "
            elif re.match(r'good afternoon', sentence, re.IGNORECASE):
                translated_text += "शुभ दोपहर" + punctuation + " "
            elif re.match(r'good evening', sentence, re.IGNORECASE):
                translated_text += "शुभ संध्या" + punctuation + " "
            elif re.match(r'good night', sentence, re.IGNORECASE):
                translated_text += "शुभ रात्रि" + punctuation + " "
            else:
                # For other text, just add a generic Hindi translation marker
                translated_text += "हिंदी अनुवाद: " + sentence + punctuation + " "
    
    elif target_lang == 'ta':
        # Tamil placeholder translations
        translated_text = "தமிழ் மொழிபெயர்ப்பு: " + placeholder_text
    
    elif target_lang == 'te':
        # Telugu placeholder translations
        translated_text = "తెలుగు అనువాదం: " + placeholder_text
    
    elif target_lang == 'ml':
        # Malayalam placeholder translations
        translated_text = "മലയാളം വിവർത്തനം: " + placeholder_text
    
    elif target_lang == 'bn':
        # Bengali placeholder translations
        translated_text = "বাংলা অনুবাদ: " + placeholder_text
    
    else:
        # Default fallback
        translated_text = placeholder_text
    
    # Step 4: Replace placeholders back with proper nouns
    for i, name in enumerate(proper_nouns):
        translated_text = translated_text.replace(f"__PROPER_NOUN_{i}__", name)
    
    logger.info(f"Translation result: {translated_text}")
    return translated_text