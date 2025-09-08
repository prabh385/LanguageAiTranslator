import os
import logging
import tempfile
import base64
from utils.fixed_translation import translate_text
import speech_recognition as sr
from gtts import gTTS

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def convert_audio_to_wav(audio_path):
    """
    Convert uploaded audio to WAV format for processing
    """
    try:
        logger.info(f"Converting audio file: {audio_path}")
        file_ext = os.path.splitext(audio_path)[1].lower()
        
        # If already a WAV file, no conversion needed
        if file_ext == '.wav':
            return audio_path
            
        # In a real implementation, we would use libraries like pydub
        # but for this demo, we'll just assume conversion works
        logger.info(f"Simulating audio conversion from {file_ext} to WAV")
        
        # Return the original path since we're not actually converting
        return audio_path
    except Exception as e:
        logger.error(f"Error converting audio: {str(e)}")
        raise

def speech_to_text(audio_path):
    """
    Convert speech from audio file to text using a speech recognition service.
    In a real implementation, this would use a service like Google Speech-to-Text,
    Amazon Transcribe, or Microsoft Azure Speech Services.
    """
    try:
        logger.info(f"Converting speech to text from {audio_path}")
        recognizer = sr.Recognizer()
        with sr.AudioFile(audio_path) as source:
            audio = recognizer.record(source)
        text = recognizer.recognize_google(audio)
        return text
    except Exception as e:
        logger.error(f"Error in speech to text conversion: {str(e)}")
        raise

def text_to_speech(text, target_lang):
    """
    Convert text to speech in the target language.
    In a real implementation, this would use a service like Google Text-to-Speech,
    Amazon Polly, or Microsoft Azure Speech Services.
    """
    try:
        logger.info(f"Converting text to speech in {target_lang}")
        
        # Create a temporary file for the audio
        temp_audio_path = tempfile.mktemp(suffix='.mp3')
        tts = gTTS(text=text, lang=target_lang)
        tts.save(temp_audio_path)
        
        return temp_audio_path
        
    except Exception as e:
        logger.error(f"Error in text to speech conversion: {str(e)}")
        raise

def process_audio(audio_path, target_lang):
    """
    Process an audio file:
    1. Convert speech to English text
    2. Translate the text to the target language
    3. Convert the translated text back to speech
    
    Returns a dictionary with the original text, translated text,
    and base64-encoded audio data.
    """
    try:
        logger.info(f"Processing audio file for translation to {target_lang}")
        wav_path = convert_audio_to_wav(audio_path)
        original_text = speech_to_text(wav_path)
        translated_text = translate_text(original_text, target_lang)
        translated_audio_path = text_to_speech(translated_text, target_lang)
        
        # Read the audio file as bytes and encode to base64 for web display
        with open(translated_audio_path, 'rb') as f:
            audio_bytes = f.read()
        audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
        
        # Clean up the temporary audio file
        if os.path.exists(translated_audio_path):
            os.remove(translated_audio_path)
        
        # Return the results including the base64-encoded audio
        return {
            'original_text': original_text,
            'translated_text': translated_text,
            'audio_data': audio_base64
        }
    except Exception as e:
        logger.error(f"Error processing audio: {str(e)}")
        raise