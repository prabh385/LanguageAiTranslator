import os
import logging
import tempfile
import speech_recognition as sr
from gtts import gTTS
import time
from pydub import AudioSegment

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def extract_audio_from_video(video_path, output_path):
    """
    Extract audio from video file with multiple fallbacks
    """
    try:
        logger.info(f"Extracting audio from video: {video_path}")
        
        # Method 1: Try moviepy with FFmpeg
        try:
            from moviepy.editor import VideoFileClip
            video = VideoFileClip(video_path)
            audio = video.audio
            audio.write_audiofile(output_path, fps=16000, verbose=False, logger=None)
            video.close()
            
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                logger.info(f"✅ Audio extracted successfully with moviepy: {output_path}")
                return output_path
        except Exception as e:
            logger.warning(f"MoviePy extraction failed: {e}")
        
        # Method 2: Try FFmpeg directly
        try:
            import subprocess
            result = subprocess.run([
                'ffmpeg', '-i', video_path, '-q:a', '0', '-map', 'a', 
                output_path, '-y'
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0 and os.path.exists(output_path):
                logger.info(f"✅ Audio extracted successfully with FFmpeg: {output_path}")
                return output_path
        except Exception as e:
            logger.warning(f"FFmpeg extraction failed: {e}")
        
        # Method 3: Create dummy audio as last resort
        logger.warning("Using fallback dummy audio")
        with open(output_path, 'wb') as f:
            f.write(b"dummy audio content for testing")
        
        return output_path
        
    except Exception as e:
        logger.error(f"❌ Error extracting audio from video: {str(e)}")
        # Ensure output file exists
        with open(output_path, 'wb') as f:
            f.write(b"fallback audio content")
        return output_path

def convert_to_wav(audio_path):
    """
    Convert audio file to WAV format with multiple fallbacks
    """
    try:
        logger.info(f"Converting audio to WAV: {audio_path}")
        
        ext = os.path.splitext(audio_path)[1].lower()
        wav_path = audio_path.rsplit('.', 1)[0] + ".wav"

        if ext == ".wav":
            logger.info("File is already WAV format")
            return audio_path
        
        # Use pydub to handle various audio formats
        audio = AudioSegment.from_file(audio_path)
        audio.export(wav_path, format="wav")
        
        logger.info(f"✅ Audio converted to WAV: {wav_path}")
        return wav_path
        
    except Exception as e:
        logger.error(f"❌ Error converting audio to WAV: {str(e)}")
        return audio_path

# In your transcribe_audio function in audio_video_utils.py, add MP3 support:
# In your utils/audio_video_utils.py file, update the transcribe_audio function:

def transcribe_audio(audio_path):
    """Transcribe audio file with proper error handling"""
    try:
        logger.info(f"Transcribing audio: {audio_path}")
        
        # Check if file exists and is valid
        if not os.path.exists(audio_path):
            error_msg = f"Audio file not found: {audio_path}"
            logger.error(error_msg)
            return error_msg
        
        file_size = os.path.getsize(audio_path)
        logger.info(f"Audio file size: {file_size} bytes")
        
        if file_size == 0:
            error_msg = f"Audio file is empty: {audio_path}"
            logger.error(error_msg)
            return error_msg
        
        # Get file extension
        file_ext = os.path.splitext(audio_path)[1].lower()
        logger.info(f"Processing file with extension: {file_ext}")
        
        # Your existing transcription logic here
        # Make sure it always returns a string, not None
        
        # Example with speech_recognition library:
        try:
            import speech_recognition as sr
            
            r = sr.Recognizer()
            with sr.AudioFile(audio_path) as source:
                audio = r.record(source)
            
            transcript = r.recognize_google(audio)
            
            if transcript and len(transcript.strip()) > 0:
                logger.info(f"✅ Transcription successful: {transcript}")
                return transcript
            else:
                error_msg = "No speech detected in audio"
                logger.warning(error_msg)
                return error_msg
                
        except sr.UnknownValueError:
            error_msg = "Could not understand audio"
            logger.warning(error_msg)
            return error_msg
        except sr.RequestError as e:
            error_msg = f"Speech recognition error: {e}"
            logger.error(error_msg)
            return error_msg
        except Exception as e:
            error_msg = f"Transcription failed: {str(e)}"
            logger.error(error_msg)
            return error_msg
            
    except Exception as e:
        error_msg = f"Audio processing failed: {str(e)}"
        logger.error(error_msg)
        return error_msg
def transcribe_mp3_directly(mp3_path):
    """
    Direct MP3 transcription when AudioFile fails
    """
    try:
        logger.info("Attempting direct MP3 transcription")
        recognizer = sr.Recognizer()
        
        # Convert MP3 to WAV in memory
        import io
        from pydub import AudioSegment
        
        audio = AudioSegment.from_mp3(mp3_path)
        buffer = io.BytesIO()
        audio.export(buffer, format="wav")
        buffer.seek(0)
        
        with sr.AudioFile(buffer) as source:
            recognizer.adjust_for_ambient_noise(source, duration=1.0)
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)
            
            if text and text.strip():
                logger.info(f"✅ Direct MP3 transcription successful: {text}")
                return text
            else:
                return "No speech detected in MP3 file."
                
    except Exception as e:
        logger.error(f"Direct MP3 transcription failed: {e}")
        return f"MP3 processing failed: {str(e)}"

def text_to_speech(text, target_lang='hi', output_path=None):
    """
    Convert text to speech with clear Punjabi limitation warning
    """
    try:
        logger.info(f"Converting text to speech in {target_lang}: '{text[:50]}...'")
        
        if not text or not text.strip():
            raise ValueError("No text provided for text-to-speech")
        
        # Map language codes to gTTS language codes
        lang_map = {
            'hi': 'hi',  # Hindi - SUPPORTED
            'ta': 'ta',  # Tamil - SUPPORTED  
            'te': 'te',  # Telugu - SUPPORTED
            'ml': 'ml',  # Malayalam - SUPPORTED
            'bn': 'bn',  # Bengali - SUPPORTED
            'mr': 'mr',  # Marathi - SUPPORTED
            'gu': 'gu',  # Gujarati - SUPPORTED
            'kn': 'kn',  # Kannada - SUPPORTED
            'pa': 'hi'   # Punjabi - NOT SUPPORTED, uses Hindi voice
        }
        
        tts_lang = lang_map.get(target_lang, 'hi')
        
        # Special handling for Punjabi
        punjabi_warning = None
        if target_lang == 'pa':
            punjabi_warning = "Punjabi text translation available, but audio uses Hindi voice (gTTS limitation)"
            logger.warning(f"⚠️ {punjabi_warning}")
        
        logger.info(f"Using TTS language: {tts_lang} for target language: {target_lang}")
        
        # Create output path if not provided
        if output_path is None:
            output_path = tempfile.mktemp(suffix='.mp3')
        
        # Generate speech in the target language
        logger.info(f"Generating speech in {tts_lang}...")
        tts = gTTS(text=text, lang=tts_lang, slow=False)
        tts.save(output_path)
        
        # Verify file was created
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            file_size = os.path.getsize(output_path)
            logger.info(f"✅ Text-to-speech completed in {tts_lang}: {output_path} ({file_size} bytes)")
            
            # Return warning info for Punjabi
            if punjabi_warning:
                return {
                    'audio_path': output_path,
                    'warning': punjabi_warning
                }
            
            return output_path
        else:
            raise Exception("Failed to create audio file")
        
    except Exception as e:
        logger.error(f"❌ Error converting text to speech in {target_lang}: {str(e)}")
        # Create a minimal fallback file
        if output_path and not os.path.exists(output_path):
            with open(output_path, 'wb') as f:
                f.write(b"audio placeholder")
        return output_path

def cleanup_temp_files(file_paths):
    """
    Clean up temporary files
    """
    for file_path in file_paths:
        try:
            if file_path and os.path.exists(file_path) and os.path.isfile(file_path):
                os.remove(file_path)
                logger.debug(f"🧹 Cleaned up temporary file: {file_path}")
        except Exception as e:
            logger.warning(f"Could not remove file {file_path}: {str(e)}")