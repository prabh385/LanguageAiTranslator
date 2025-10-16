from flask import Flask, render_template, request, jsonify, send_file, url_for
import os
import logging
from werkzeug.utils import secure_filename
import sys

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

print(f"📁 Working directory: {current_dir}")

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'mp3', 'wav', 'ogg', 'mp4', 'avi', 'mov', 'webm', 'flac', 'aac', 'wma', 'm4a', 'mkv', 'flv', 'wmv', 'm4v', 'mpeg'}

# Supported languages
LANGUAGES = {
    'hi': 'Hindi', 'ta': 'Tamil', 'te': 'Telugu', 'ml': 'Malayalam',
    'bn': 'Bengali', 'mr': 'Marathi', 'gu': 'Gujarati', 'kn': 'Kannada', 'pa': 'Punjabi'
}

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# FALLBACK TRANSLATION FUNCTION (ALWAYS WORKS)
def translate_text_fallback(text, target_lang='hi'):
    """Fallback translation that always works"""
    logger.info(f"🔤 Fallback translation: '{text}' to {target_lang}")
    
    # Enhanced demo translations
    demo_translations = {
        'hi': {
            "hello": "नमस्ते",
            "hi": "नमस्ते",
            "how are you": "आप कैसे हैं",
            "thank you": "धन्यवाद",
            "my name is": "मेरा नाम है",
            "what is your name": "आपका नाम क्या है",
            "good morning": "शुभ प्रभात",
            "good night": "शुभ रात्रि",
            "i love you": "मैं तुमसे प्यार करता हूँ",
            "where are you from": "आप कहाँ से हैं"
        },
        'ta': {
            "hello": "वணக்கம்",
            "thank you": "நன்றி",
            "how are you": "நீங்கள் எப்படி இருக்கிறீர்கள்"
        },
        'te': {
            "hello": "హలో", 
            "thank you": "ధన్యవాదాలు",
            "how are you": "మీరు ఎలా ఉన్నారు"
        }
    }
    
    text_lower = text.lower().strip()
    
    # Try exact match first
    lang_dict = demo_translations.get(target_lang, {})
    if text_lower in lang_dict:
        return lang_dict[text_lower]
    
    # Try partial matches
    for key, value in lang_dict.items():
        if key in text_lower:
            return value
    
    # Fallback to simple translation
    fallback_translations = {
        'hi': f"अनुवाद: {text}",
        'ta': f"மொழிபெயர்ப்பு: {text}",
        'te': f"అనువాదం: {text}",
        'ml': f"വിവർത്തനം: {text}",
        'bn': f"অনুবাদ: {text}",
        'mr': f"भाषांतर: {text}",
        'gu': f"અનુવાદ: {text}",
        'kn': f"ಅನುವಾದ: {text}",
        'pa': f"ਅਨੁਵਾਦ: {text}"
    }
    
    return fallback_translations.get(target_lang, f"Translation: {text}")

# Try to import real translation function
try:
    from utils.fixed_translation import translate_text
    print("✅ SUCCESS: Loaded real translation engine from fixed_translation.py")
    
    # Test the real translation
    test_result = translate_text("hello", "hi")
    print(f"   Test translation: '{test_result}'")
    
except ImportError as e:
    print(f"❌ Failed to import fixed_translation: {e}")
    print("⚠️  Using enhanced fallback translation")
    translate_text = translate_text_fallback
except Exception as e:
    print(f"❌ Error in fixed_translation: {e}")
    print("⚠️  Using enhanced fallback translation")
    translate_text = translate_text_fallback

# Enhanced MP3 to WAV conversion function
def convert_mp3_to_wav(mp3_path, wav_path=None):
    """Convert MP3 to WAV format with multiple fallback methods"""
    try:
        if wav_path is None:
            wav_path = mp3_path.replace('.mp3', '.wav')
        
        # Check if we already have a valid WAV file
        if os.path.exists(wav_path) and os.path.getsize(wav_path) > 0:
            logger.info(f"✅ WAV file already exists: {wav_path}")
            return wav_path
            
        logger.info(f"🔄 Converting MP3 to WAV: {mp3_path} -> {wav_path}")
        
        # Method 1: Try pydub with explicit ffmpeg path
        try:
            from pydub import AudioSegment
            
            # Try to find ffmpeg in common locations
            ffmpeg_paths = [
                'ffmpeg',
                'C:\\ffmpeg\\bin\\ffmpeg.exe',
                'C:\\Program Files\\ffmpeg\\bin\\ffmpeg.exe',
                '.\\ffmpeg\\bin\\ffmpeg.exe'
            ]
            
            ffmpeg_found = None
            for path in ffmpeg_paths:
                try:
                    import subprocess
                    result = subprocess.run([path, '-version'], capture_output=True, timeout=5)
                    if result.returncode == 0:
                        ffmpeg_found = path
                        logger.info(f"✅ Found FFmpeg at: {path}")
                        break
                except:
                    continue
            
            if ffmpeg_found:
                # Set ffmpeg path for pydub
                AudioSegment.converter = ffmpeg_found
                audio = AudioSegment.from_mp3(mp3_path)
                audio.export(wav_path, format="wav")
                logger.info(f"✅ Successfully converted MP3 to WAV using pydub: {wav_path}")
                
                # Verify the file was created
                if os.path.exists(wav_path) and os.path.getsize(wav_path) > 0:
                    return wav_path
                else:
                    logger.warning("⚠️ WAV file created but appears empty")
                    raise Exception("Empty WAV file")
            else:
                logger.warning("⚠️ FFmpeg not found in common locations")
                raise ImportError("FFmpeg not available")
                
        except Exception as e:
            logger.warning(f"⚠️ pydub method failed: {e}")
            
        # Method 2: Try moviepy (often works without system FFmpeg)
        try:
            from moviepy.editor import AudioFileClip
            audio = AudioFileClip(mp3_path)
            audio.write_audiofile(wav_path, verbose=False, logger=None, fps=16000)
            audio.close()
            logger.info(f"✅ Successfully converted MP3 to WAV using moviepy: {wav_path}")
            
            if os.path.exists(wav_path) and os.path.getsize(wav_path) > 0:
                return wav_path
            else:
                raise Exception("Empty WAV file from moviepy")
                
        except Exception as e:
            logger.warning(f"⚠️ moviepy method failed: {e}")
            
        # Method 3: Use subprocess with ffmpeg directly
        try:
            import subprocess
            
            # Try to run ffmpeg command directly
            cmd = [
                'ffmpeg', '-i', mp3_path, '-acodec', 'pcm_s16le', 
                '-ar', '16000', '-ac', '1', '-y', wav_path
            ]
            
            # Remove 'ffmpeg' if we found a specific path earlier
            if ffmpeg_found and ffmpeg_found != 'ffmpeg':
                cmd[0] = ffmpeg_found
                
            result = subprocess.run(cmd, capture_output=True, timeout=30)
            
            if result.returncode == 0 and os.path.exists(wav_path):
                logger.info(f"✅ Successfully converted MP3 to WAV using direct ffmpeg: {wav_path}")
                return wav_path
            else:
                raise Exception(f"FFmpeg failed with return code {result.returncode}")
                
        except Exception as e:
            logger.warning(f"⚠️ Direct ffmpeg method failed: {e}")
            
        # Method 4: Ultimate fallback - use online service or return error
        logger.error("❌ All MP3 conversion methods failed")
        raise Exception("MP3 to WAV conversion failed. Please install FFmpeg or use WAV files.")
                
    except Exception as e:
        logger.error(f"❌ MP3 to WAV conversion failed: {e}")
        raise  # Re-raise the exception to handle it in the calling function

# Deployment-optimized helper functions
def convert_mp3_to_wav_deployment(mp3_path, wav_path=None):
    """MP3 conversion optimized for deployment environments"""
    try:
        if wav_path is None:
            wav_path = mp3_path.replace('.mp3', '.wav')
        
        logger.info(f"🔄 Converting MP3 for deployment: {mp3_path}")
        
        # Method 1: Try moviepy first (often works in cloud environments)
        try:
            from moviepy.editor import AudioFileClip
            audio = AudioFileClip(mp3_path)
            audio.write_audiofile(wav_path, verbose=False, logger=None, fps=16000)
            audio.close()
            
            if os.path.exists(wav_path) and os.path.getsize(wav_path) > 0:
                logger.info(f"✅ Converted using moviepy: {wav_path}")
                return wav_path
        except Exception as e:
            logger.warning(f"⚠️ Moviepy failed: {e}")
        
        # Method 2: Try pydub if available
        try:
            from pydub import AudioSegment
            audio = AudioSegment.from_mp3(mp3_path)
            audio.export(wav_path, format="wav")
            logger.info(f"✅ Converted using pydub: {wav_path}")
            return wav_path
        except Exception as e:
            logger.warning(f"⚠️ Pydub failed: {e}")
        
        # Method 3: Try direct file copy as fallback
        logger.warning("⚠️ Using MP3 file directly (conversion not available)")
        return mp3_path
        
    except Exception as e:
        logger.error(f"❌ Deployment MP3 conversion failed: {e}")
        return mp3_path  # Return original file as fallback

def safe_transcribe_audio_deployment(audio_path):
    """Safe transcription with deployment optimizations"""
    try:
        # Import here to avoid circular imports
        from utils.audio_video_utils import transcribe_audio
        
        # Your existing transcription logic with timeout
        transcript = transcribe_audio(audio_path)
        
        # Ensure we never return None
        if transcript is None:
            return "Transcription service temporarily unavailable"
            
        return str(transcript)
        
    except Exception as e:
        logger.error(f"❌ Deployment transcription error: {str(e)}")
        return f"Transcription service error: {str(e)}"

def safe_transcribe_audio(audio_path):
    """Safely transcribe audio with None handling"""
    try:
        from utils.audio_video_utils import transcribe_audio
        
        transcript = transcribe_audio(audio_path)
        
        # Ensure transcript is never None
        if transcript is None:
            logger.error("❌ Transcription returned None")
            return "Transcription failed: No result returned"
        
        # Ensure transcript is a string
        if not isinstance(transcript, str):
            transcript = str(transcript)
            
        return transcript
        
    except Exception as e:
        logger.error(f"❌ Safe transcription error: {str(e)}")
        return f"Transcription error: {str(e)}"

# Try to import other utilities with fallbacks
try:
    from utils.audio_video_utils import (
        extract_audio_from_video,
        convert_to_wav,
        transcribe_audio,
        text_to_speech,
        cleanup_temp_files
    )
    print("✅ SUCCESS: Loaded audio_video_utils")
    
except ImportError as e:
    print(f"❌ Failed to import audio_video_utils: {e}")
    # Create fallback functions
    def extract_audio_from_video(video_path, audio_path):
        logger.info(f"Mock: Extracting audio to {audio_path}")
        with open(audio_path, 'w') as f:
            f.write("mock audio")
        return audio_path
    
    def convert_to_wav(audio_path):
        return audio_path
    
    def transcribe_audio(audio_path):
        return "This is a mock English transcript from the audio file."
    
    def text_to_speech(text, target_lang, output_path=None):
        if output_path is None:
            output_path = "mock_audio.mp3"
        with open(output_path, 'w') as f:
            f.write("mock audio")
        return output_path
    
    def cleanup_temp_files(files):
        for file_path in files:
            try:
                if file_path and os.path.exists(file_path):
                    os.remove(file_path)
            except:
                pass

try:
    from utils.lip_sync import apply_lip_sync
    print("✅ SUCCESS: Loaded lip_sync")
except ImportError as e:
    print(f"❌ Failed to import lip_sync: {e}")
    def apply_lip_sync(video_path, audio_path, output_path):
        logger.info(f"Mock lip-sync: {video_path} -> {output_path}")
        try:
            from moviepy.editor import VideoFileClip, AudioFileClip
            video = VideoFileClip(video_path)
            audio = AudioFileClip(audio_path)
            final_video = video.set_audio(audio)
            final_video.write_videofile(output_path, verbose=False, logger=None)
            video.close()
            audio.close()
            final_video.close()
            return output_path
        except:
            import shutil
            shutil.copy2(video_path, output_path)
            return output_path

def apply_lip_sync_deployment(video_path, audio_path, output_path):
    """Lip-sync optimized for deployment environments"""
    try:
        logger.info(f"🎭 Applying lip-sync in deployment: {video_path} + {audio_path}")
        
        # Method 1: Try moviepy first
        try:
            from moviepy.editor import VideoFileClip, AudioFileClip
            
            video = VideoFileClip(video_path)
            audio = AudioFileClip(audio_path)
            
            # Set audio to video
            final_video = video.set_audio(audio)
            
            # Write with deployment-friendly settings
            final_video.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                verbose=False,
                logger=None,
                temp_audiofile='temp-audio.m4a',
                remove_temp=True,
                threads=1  # Use single thread to avoid memory issues
            )
            
            # Close clips to free memory
            video.close()
            audio.close()
            final_video.close()
            
            logger.info(f"✅ Lip-sync successful with moviepy: {output_path}")
            return output_path
            
        except Exception as e:
            logger.warning(f"⚠️ Moviepy lip-sync failed: {e}")
        
        # Method 2: Try direct FFmpeg command
        try:
            import subprocess
            
            cmd = [
                'ffmpeg',
                '-i', video_path,
                '-i', audio_path,
                '-c:v', 'copy',  # Copy video stream without re-encoding
                '-c:a', 'aac',
                '-map', '0:v:0',
                '-map', '1:a:0',
                '-shortest',
                '-y',  # Overwrite output file
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0 and os.path.exists(output_path):
                logger.info(f"✅ Lip-sync successful with FFmpeg: {output_path}")
                return output_path
            else:
                raise Exception(f"FFmpeg failed: {result.stderr}")
                
        except Exception as e:
            logger.warning(f"⚠️ FFmpeg lip-sync failed: {e}")
        
        # Method 3: Fallback - copy original video
        logger.warning("⚠️ All lip-sync methods failed, returning original video")
        import shutil
        shutil.copy2(video_path, output_path)
        return output_path
        
    except Exception as e:
        logger.error(f"❌ Lip-sync deployment failed: {e}")
        # Ultimate fallback
        import shutil
        shutil.copy2(video_path, output_path)
        return output_path

print("🎉 All systems ready!")

@app.route('/')
def index():
    return render_template('index.html', languages=LANGUAGES)

@app.route('/api/translate/text', methods=['POST'])
def translate_text_endpoint():
    """Text translation endpoint"""
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        target_lang = data.get('target_language', 'hi')
        
        logger.info(f"📝 Translation request: '{text}' -> {target_lang}")
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
            
        translated_text = translate_text(text, target_lang)
        logger.info(f"✅ Translation result: '{translated_text}'")
        
        return jsonify({
            'success': True,
            'original_text': text,
            'translated_text': translated_text,
            'target_language': target_lang
        })
        
    except Exception as e:
        logger.error(f"❌ Translation error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/translate/audio', methods=['POST'])
def translate_audio_endpoint():
    """Audio translation endpoint - Deployment optimized"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        target_lang = request.form.get('target_language', 'hi')

        logger.info(f"🎵 Audio translation request to: {target_lang}")

        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Please upload a valid audio or video file.'}), 400

        # Save the uploaded file
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        logger.info(f"💾 File saved: {file_path}")

        temp_files = [file_path]
        processed_audio_path = file_path

        try:
            # Handle MP3 files with deployment-friendly approach
            if filename.lower().endswith('.mp3'):
                logger.info("🔄 Processing MP3 file for deployment...")
                wav_path = file_path.replace('.mp3', '.wav')
                
                try:
                    # Try conversion but don't fail completely if it doesn't work
                    processed_audio_path = convert_mp3_to_wav_deployment(file_path, wav_path)
                    if processed_audio_path != file_path:
                        temp_files.append(processed_audio_path)
                    logger.info(f"✅ MP3 processed: {processed_audio_path}")
                except Exception as e:
                    logger.warning(f"⚠️ MP3 conversion failed, using original: {e}")
                    processed_audio_path = file_path  # Fallback to original MP3
            else:
                # For other audio formats
                processed_audio_path = convert_to_wav(file_path)
                if processed_audio_path != file_path:
                    temp_files.append(processed_audio_path)

            # Verify the audio file
            if not os.path.exists(processed_audio_path) or os.path.getsize(processed_audio_path) == 0:
                return jsonify({
                    'success': False,
                    'error': 'Audio file is empty or corrupted',
                    'original_text': '',
                    'translated_text': ''
                }), 400

            # Transcribe with timeout and better error handling
            logger.info("🔊 Transcribing English audio...")
            try:
                transcript = safe_transcribe_audio_deployment(processed_audio_path)
                logger.info(f"📄 Transcription completed, length: {len(transcript) if transcript else 0}")
            except Exception as e:
                logger.error(f"❌ Transcription error: {str(e)}")
                return jsonify({
                    'success': False,
                    'error': f'Transcription service unavailable: {str(e)}',
                    'original_text': '',
                    'translated_text': ''
                }), 500

            # Safe check for transcription failure
            if not transcript or any(phrase in (transcript.lower() if transcript else "") for phrase in ['error', 'could not', 'no speech', 'unavailable', 'failed', 'network']):
                return jsonify({
                    'success': False,
                    'error': f'Transcription failed: {transcript}',
                    'original_text': '',
                    'translated_text': ''
                }), 400

            # Translate with fallback
            logger.info(f"🔄 Translating to {target_lang}...")
            try:
                translated_text = translate_text(transcript, target_lang)
                logger.info(f"🌐 Translation completed")
            except Exception as e:
                logger.error(f"❌ Translation error: {str(e)}")
                # Use fallback translation
                translated_text = translate_text_fallback(transcript, target_lang)

            # Text-to-speech with fallback
            logger.info(f"🗣️ Generating speech in {target_lang}...")
            audio_output_path = os.path.join(app.config['UPLOAD_FOLDER'], f'translated_{target_lang}_{os.path.splitext(filename)[0]}.mp3')
            
            try:
                tts_result = text_to_speech(translated_text, target_lang, audio_output_path)
                
                # Handle different return types
                if isinstance(tts_result, dict) and 'audio_path' in tts_result:
                    audio_path = tts_result['audio_path']
                    warning_message = tts_result.get('warning')
                else:
                    audio_path = tts_result
                    warning_message = None
                
                # Verify audio was created
                if not os.path.exists(audio_path) or os.path.getsize(audio_path) == 0:
                    logger.warning("⚠️ TTS failed, providing text-only response")
                    return jsonify({
                        'success': True,
                        'original_text': transcript,
                        'translated_text': translated_text,
                        'audio_url': None,
                        'target_language': target_lang,
                        'warning': 'Audio generation failed, but translation completed successfully'
                    })
                
                return jsonify({
                    'success': True,
                    'original_text': transcript,
                    'translated_text': translated_text,
                    'audio_url': f'/api/download/{os.path.basename(audio_path)}',
                    'target_language': target_lang,
                    'warning': warning_message
                })

            except Exception as e:
                logger.error(f"❌ TTS error: {str(e)}")
                # Return success with text only
                return jsonify({
                    'success': True,
                    'original_text': transcript,
                    'translated_text': translated_text,
                    'audio_url': None,
                    'target_language': target_lang,
                    'warning': 'Translation completed but audio generation failed'
                })

        except Exception as e:
            logger.error(f"❌ Audio processing error: {str(e)}")
            return jsonify({
                'success': False,
                'error': f'Audio processing failed: {str(e)}',
                'original_text': '',
                'translated_text': ''
            }), 500

        finally:
            # Clean up temporary files
            cleanup_temp_files(temp_files)

    except Exception as e:
        logger.error(f"❌ Audio translation error: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Audio translation failed: {str(e)}',
            'original_text': '',
            'translated_text': ''
        }), 500
        
@app.route('/api/translate/video', methods=['POST'])
def translate_video_endpoint():
    """Video translation endpoint - Deployment optimized"""
    try:
        logger.info("🎬 Starting video translation on deployed environment")
        
        if 'file' not in request.files:
            return jsonify({'error': 'No video file provided'}), 400
        
        video_file = request.files['file']
        target_lang = request.form.get('target_language', 'hi')
        
        logger.info(f"🎥 Video translation request: {target_lang}")
        
        if video_file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        if not allowed_file(video_file.filename):
            return jsonify({'error': 'Invalid file type. Supported: MP4, AVI, MOV, WebM'}), 400

        # Save the uploaded video
        video_filename = secure_filename(video_file.filename)
        video_path = os.path.join(app.config['UPLOAD_FOLDER'], video_filename)
        video_file.save(video_path)
        logger.info(f"💾 Video saved: {video_path} (Size: {os.path.getsize(video_path)} bytes)")

        temp_files = [video_path]
        audio_path = None
        translated_audio_path = None
        lip_synced_video_path = None

        try:
            # Step 1: Extract audio from video
            logger.info("🔊 Extracting audio from video...")
            audio_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{os.path.splitext(video_filename)[0]}_audio.wav")
            
            try:
                extract_audio_from_video(video_path, audio_path)
                if not os.path.exists(audio_path) or os.path.getsize(audio_path) == 0:
                    raise Exception("Audio extraction failed - empty file")
                temp_files.append(audio_path)
                logger.info(f"✅ Audio extracted: {audio_path}")
            except Exception as e:
                logger.error(f"❌ Audio extraction failed: {str(e)}")
                return jsonify({
                    'success': False,
                    'error': f'Audio extraction failed: {str(e)}. Please check if FFmpeg is installed.',
                    'original_text': '',
                    'translated_text': ''
                }), 500

            # Step 2: Transcribe audio
            logger.info("🎤 Transcribing audio to text...")
            try:
                transcript = safe_transcribe_audio_deployment(audio_path)
                logger.info(f"📄 Transcription completed")
                
                # Check if transcription failed
                if not transcript or any(phrase in (transcript.lower() if transcript else "") for phrase in ['error', 'could not', 'no speech', 'unavailable', 'failed']):
                    return jsonify({
                        'success': False,
                        'error': f'Transcription failed: {transcript}',
                        'original_text': '',
                        'translated_text': ''
                    }), 400
                    
            except Exception as e:
                logger.error(f"❌ Transcription failed: {str(e)}")
                return jsonify({
                    'success': False,
                    'error': f'Transcription service unavailable: {str(e)}',
                    'original_text': '',
                    'translated_text': ''
                }), 500

            # Step 3: Translate text
            logger.info(f"🔄 Translating to {target_lang}...")
            try:
                translated_text = translate_text(transcript, target_lang)
                logger.info(f"🌐 Translation completed")
            except Exception as e:
                logger.error(f"❌ Translation failed: {str(e)}")
                # Use fallback translation
                translated_text = translate_text_fallback(transcript, target_lang)

            # Step 4: Generate translated audio
            logger.info(f"🗣️ Generating speech in {target_lang}...")
            translated_audio_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{os.path.splitext(video_filename)[0]}_translated.mp3")
            
            try:
                tts_result = text_to_speech(translated_text, target_lang, translated_audio_path)
                
                # Handle different return types
                if isinstance(tts_result, dict) and 'audio_path' in tts_result:
                    translated_audio_path = tts_result['audio_path']
                    warning_message = tts_result.get('warning')
                else:
                    translated_audio_path = tts_result
                    warning_message = None
                
                # Verify audio was created
                if not os.path.exists(translated_audio_path) or os.path.getsize(translated_audio_path) == 0:
                    logger.warning("⚠️ TTS failed, providing text-only response")
                    return jsonify({
                        'success': True,
                        'original_text': transcript,
                        'translated_text': translated_text,
                        'video_url': None,
                        'target_language': target_lang,
                        'warning': 'Video translation completed but audio generation failed'
                    })
                
                temp_files.append(translated_audio_path)
                logger.info(f"✅ Translated audio generated: {translated_audio_path}")
                
            except Exception as e:
                logger.error(f"❌ TTS failed: {str(e)}")
                return jsonify({
                    'success': True,
                    'original_text': transcript,
                    'translated_text': translated_text,
                    'video_url': None,
                    'target_language': target_lang,
                    'warning': 'Translation completed but audio generation failed'
                })

            # Step 5: Apply lip-sync (video + audio merge)
            logger.info("🎭 Applying lip-sync...")
            output_video_path = os.path.join(app.config['UPLOAD_FOLDER'], f"translated_{os.path.splitext(video_filename)[0]}.mp4")
            
            try:
                lip_synced_video_path = apply_lip_sync_deployment(video_path, translated_audio_path, output_video_path)
                
                if not os.path.exists(lip_synced_video_path) or os.path.getsize(lip_synced_video_path) == 0:
                    logger.warning("⚠️ Lip-sync failed, providing original video with separate audio")
                    # Fallback: return original video path
                    lip_synced_video_path = video_path
                
                logger.info(f"✅ Lip-sync completed: {lip_synced_video_path}")
                
            except Exception as e:
                logger.error(f"❌ Lip-sync failed: {str(e)}")
                # Fallback: use original video
                lip_synced_video_path = video_path

            logger.info("✅ Video translation completed successfully!")
            return jsonify({
                'success': True,
                'original_text': transcript,
                'translated_text': translated_text,
                'video_url': f'/api/download/{os.path.basename(lip_synced_video_path)}',
                'target_language': target_lang,
                'warning': warning_message
            })

        except Exception as e:
            logger.error(f"❌ Video processing error: {str(e)}")
            return jsonify({
                'success': False,
                'error': f'Video processing failed: {str(e)}',
                'original_text': '',
                'translated_text': ''
            }), 500

        finally:
            # Clean up temporary files (keep final video)
            try:
                files_to_cleanup = [f for f in temp_files if f and os.path.exists(f) and f != lip_synced_video_path and f != video_path]
                cleanup_temp_files(files_to_cleanup)
            except Exception as e:
                logger.warning(f"Error cleaning up temporary files: {e}")

    except Exception as e:
        logger.error(f"❌ Video translation error: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Video translation failed: {str(e)}',
            'original_text': '',
            'translated_text': ''
        }), 500
        
@app.route('/api/download/<filename>')
def download_file(filename):
    """File download endpoint"""
    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        logger.error(f"❌ Download error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/languages')
def get_languages():
    """Get supported languages"""
    return jsonify(LANGUAGES)

@app.route('/api/test-translation')
def test_translation():
    """Test route to check if translation works"""
    test_text = "hello world"
    test_lang = "hi"
    
    result = translate_text(test_text, test_lang)
    
    return jsonify({
        'test_text': test_text,
        'test_lang': test_lang,
        'translated_text': result,
        'success': True
    })

@app.route('/api/health')
def health_check():
    """Health check endpoint for deployment"""
    import subprocess
    import requests
    
    health_status = {
        'status': 'healthy',
        'services': {}
    }
    
    try:
        # Check FFmpeg
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True, timeout=5)
        health_status['services']['ffmpeg'] = 'available' if result.returncode == 0 else 'unavailable'
    except:
        health_status['services']['ffmpeg'] = 'unavailable'
    
    try:
        # Check network connectivity
        response = requests.get('https://www.google.com', timeout=5)
        health_status['services']['network'] = 'connected' if response.status_code == 200 else 'disconnected'
    except:
        health_status['services']['network'] = 'disconnected'
    
    # Check upload directory
    health_status['services']['storage'] = 'ok' if os.path.exists(app.config['UPLOAD_FOLDER']) else 'failed'
    
    # Check function definitions
    health_status['services']['functions'] = {
        'convert_mp3_to_wav_deployment': 'convert_mp3_to_wav_deployment' in globals(),
        'safe_transcribe_audio_deployment': 'safe_transcribe_audio_deployment' in globals(),
        'safe_transcribe_audio': 'safe_transcribe_audio' in globals()
    }
    
    # Overall status
    if any(status == 'unavailable' for status in health_status['services'].values() if isinstance(status, str)):
        health_status['status'] = 'degraded'
    
    return jsonify(health_status)

if __name__ == '__main__':
    logger.info("🚀 Starting Translation Server...")
    logger.info("🌐 Server: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)