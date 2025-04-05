import os
import logging
from pydub import AudioSegment
from moviepy.editor import VideoFileClip
import tempfile
import speech_recognition as sr
from gtts import gTTS
from utils.fixed_translation import translate_text
import time

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def extract_audio_from_video(video_path, output_path):
    """
    Extract audio from video file and save as WAV file.
    
    Args:
        video_path (str): Path to the video file
        output_path (str): Path to save the audio file
        
    Returns:
        str: Path to the audio file
    """
    try:
        # Extract audio from video
        video = VideoFileClip(video_path)
        video.audio.write_audiofile(output_path, codec='pcm_s16le')
        video.close()
        
        return output_path
    except Exception as e:
        logger.error(f"Error extracting audio from video: {str(e)}")
        raise

def convert_to_wav(audio_path):
    """
    Convert audio file to WAV format if needed.
    
    Args:
        audio_path (str): Path to the audio file
        
    Returns:
        str: Path to the WAV file
    """
    try:
        # Create a temporary file for the WAV
        temp_wav = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        temp_wav_path = temp_wav.name
        temp_wav.close()
        
        # Convert to WAV
        audio = AudioSegment.from_file(audio_path)
        audio.export(temp_wav_path, format="wav")
        
        return temp_wav_path
    except Exception as e:
        logger.error(f"Error converting audio to WAV: {str(e)}")
        raise

def transcribe_audio(audio_path):
    """
    Transcribe audio file using speech recognition.
    
    Args:
        audio_path (str): Path to the audio file
        
    Returns:
        str: Transcribed text
    """
    try:
        recognizer = sr.Recognizer()
        max_retries = 3
        retry_delay = 2  # seconds
        
        with sr.AudioFile(audio_path) as source:
            audio_data = recognizer.record(source)
            
            # Try to transcribe with retries
            for attempt in range(max_retries):
                try:
                    text = recognizer.recognize_google(audio_data)
                    if not text or not text.strip():
                        raise sr.UnknownValueError("No speech detected in the audio")
                    return text
                except sr.UnknownValueError:
                    logger.warning("Speech recognition could not understand the audio")
                    if attempt == max_retries - 1:
                        return "No speech detected in the audio. Please ensure the video contains clear speech."
                except sr.RequestError as e:
                    logger.warning(f"Speech recognition request failed (attempt {attempt + 1}/{max_retries}): {str(e)}")
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                    else:
                        return "Speech recognition service unavailable. Please check your internet connection and try again."
                except Exception as e:
                    logger.error(f"Unexpected error during speech recognition: {str(e)}")
                    if attempt == max_retries - 1:
                        return f"Error during speech recognition: {str(e)}"
                    time.sleep(retry_delay)
                    
        return "Failed to transcribe audio after multiple attempts. Please try again."
    except Exception as e:
        logger.error(f"Error transcribing audio: {str(e)}")
        raise

def text_to_speech(text, output_path):
    """
    Convert text to speech using gTTS.
    
    Args:
        text (str): Text to convert to speech
        output_path (str): Path to save the audio file
        
    Returns:
        str: Path to the audio file
    """
    try:
        # Convert text to speech
        tts = gTTS(text=text, lang='hi')  # Default to Hindi
        tts.save(output_path)
        
        return output_path
    except Exception as e:
        logger.error(f"Error converting text to speech: {str(e)}")
        raise

def cleanup_temp_files(file_paths):
    """
    Clean up temporary files.
    
    Args:
        file_paths (list): List of file paths to delete
    """
    for file_path in file_paths:
        try:
            if os.path.exists(file_path):
                os.unlink(file_path)
        except Exception as e:
            logger.warning(f"Error deleting temporary file {file_path}: {str(e)}") 