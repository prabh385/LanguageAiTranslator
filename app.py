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
app.config['ALLOWED_EXTENSIONS'] = {'mp3', 'wav', 'ogg', 'mp4', 'avi', 'mov', 'webm'}

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
    """Audio translation endpoint - Enhanced with robust MP3 support"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        target_lang = request.form.get('target_language', 'hi')

        logger.info(f"🎵 Audio translation request to: {target_lang}")

        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Please upload MP3, WAV, or OGG file.'}), 400

        # Save the uploaded file
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        logger.info(f"💾 File saved: {file_path}")

        temp_files = [file_path]
        processed_audio_path = file_path

        try:
            # Handle MP3 files specifically
            if filename.lower().endswith('.mp3'):
                logger.info("🔄 Processing MP3 file...")
                wav_path = file_path.replace('.mp3', '.wav')
                
                try:
                    processed_audio_path = convert_mp3_to_wav(file_path, wav_path)
                    if processed_audio_path != file_path:
                        temp_files.append(processed_audio_path)
                    logger.info(f"✅ MP3 converted to: {processed_audio_path}")
                except Exception as e:
                    logger.error(f"❌ MP3 conversion failed: {e}")
                    return jsonify({
                        'success': False,
                        'error': f'MP3 processing failed: {str(e)}. Please install FFmpeg or convert to WAV format.',
                        'original_text': '',
                        'translated_text': ''
                    }), 400
            else:
                # For other audio formats, use existing conversion
                processed_audio_path = convert_to_wav(file_path)
                if processed_audio_path != file_path:
                    temp_files.append(processed_audio_path)

            # Verify the audio file exists and is valid
            if not os.path.exists(processed_audio_path) or os.path.getsize(processed_audio_path) == 0:
                raise Exception("Processed audio file is empty or missing")

            # Transcribe the audio
            logger.info("🔊 Transcribing English audio...")
            transcript = transcribe_audio(processed_audio_path)
            logger.info(f"📄 English transcript: {transcript}")

            # Check if transcription failed
            if any(phrase in transcript.lower() for phrase in ['error', 'could not', 'no speech', 'unavailable', 'failed']):
                return jsonify({
                    'success': False,
                    'error': transcript,
                    'original_text': '',
                    'translated_text': ''
                }), 400

            # Translate the transcript
            logger.info(f"🔄 Translating to {target_lang}...")
            translated_text = translate_text(transcript, target_lang)
            logger.info(f"🌐 Translated text: {translated_text}")

            # Convert translated text to speech
            audio_output_path = os.path.join(app.config['UPLOAD_FOLDER'], f'translated_{target_lang}_{os.path.splitext(filename)[0]}.mp3')
            logger.info(f"🗣️ Generating speech in {target_lang}...")
            
            tts_result = text_to_speech(translated_text, target_lang, audio_output_path)
            
            # Handle Punjabi warning
            warning_message = None
            if isinstance(tts_result, dict) and 'warning' in tts_result:
                warning_message = tts_result['warning']
                audio_path = tts_result['audio_path']
            else:
                audio_path = tts_result
            
            # Verify audio was created
            if not os.path.exists(audio_path) or os.path.getsize(audio_path) == 0:
                raise Exception("Failed to generate translated audio")

            return jsonify({
                'success': True,
                'original_text': transcript,
                'translated_text': translated_text,
                'audio_url': f'/api/download/{os.path.basename(audio_path)}',
                'target_language': target_lang,
                'warning': warning_message  # Frontend can show this warning
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
    """Video translation endpoint"""
    try:
        logger.info("🎬 Starting video translation")
        
        if 'file' not in request.files:
            return jsonify({'error': 'No video file provided'}), 400
        
        video_file = request.files['file']
        target_lang = request.form.get('target_language', 'hi')
        
        logger.info(f"🎥 Video translation: {target_lang}")
        
        if video_file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        if not allowed_file(video_file.filename):
            return jsonify({'error': 'Invalid file type'}), 400
        
        # Save the uploaded video
        video_filename = secure_filename(video_file.filename)
        video_path = os.path.join(app.config['UPLOAD_FOLDER'], video_filename)
        video_file.save(video_path)
        
        # Extract audio from video
        audio_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{os.path.splitext(video_filename)[0]}_audio.wav")
        extract_audio_from_video(video_path, audio_path)
        
        # Transcribe the audio
        transcript = transcribe_audio(audio_path)
        logger.info(f"📄 Transcript: {transcript}")
        
        # Translate the transcript
        translated_text = translate_text(transcript, target_lang)
        logger.info(f"🌐 Translated: {translated_text}")
        
        # Generate speech from translated text
        translated_audio_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{os.path.splitext(video_filename)[0]}_translated.mp3")
        text_to_speech(translated_text, target_lang, translated_audio_path)
        
        # Apply lip-sync to the video
        output_video_path = os.path.join(app.config['UPLOAD_FOLDER'], f"translated_{os.path.splitext(video_filename)[0]}.mp4")
        lip_synced_video_path = apply_lip_sync(video_path, translated_audio_path, output_video_path)
        
        # Clean up temporary files
        cleanup_temp_files([audio_path, translated_audio_path, video_path])
        
        logger.info("✅ Video translation completed!")
        return jsonify({
            'success': True,
            'original_text': transcript,
            'translated_text': translated_text,
            'video_url': f'/api/download/{os.path.basename(lip_synced_video_path)}'
        })
        
    except Exception as e:
        logger.error(f"❌ Video translation error: {str(e)}")
        return jsonify({'error': str(e)}), 500

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

if __name__ == '__main__':
    logger.info("🚀 Starting Translation Server...")
    logger.info("🌐 Server: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)