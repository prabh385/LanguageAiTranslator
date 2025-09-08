from flask import Flask, render_template, request, jsonify, send_file, url_for
import os
import logging
from werkzeug.utils import secure_filename
from utils.fixed_translation import translate_text
from utils.audio_video_utils import (
    extract_audio_from_video,
    convert_to_wav,
    transcribe_audio,
    text_to_speech,
    cleanup_temp_files
)
import tempfile
from dotenv import load_dotenv
from moviepy.editor import VideoFileClip, AudioFileClip
from utils.lip_sync import apply_lip_sync

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'mp3', 'wav', 'mp4', 'avi', 'mov'}

# Supported languages
LANGUAGES = {
    'hi': 'Hindi',
    'ta': 'Tamil',
    'te': 'Telugu',
    'ml': 'Malayalam',
    'bn': 'Bengali'
}

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template('index.html', languages=LANGUAGES)

@app.route('/translate/text', methods=['POST'])
def translate_text_route():
    try:
        data = request.get_json()
        text = data.get('text', '')
        target_lang = data.get('target_lang', 'hi')
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
            
        translated_text = translate_text(text, target_lang)
        return jsonify({'translated_text': translated_text})
        
    except Exception as e:
        logger.error(f"Error in text translation: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/translate/audio', methods=['POST'])
def translate_audio_route():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        target_lang = request.form.get('target_lang', 'hi')

        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type'}), 400

        # Save the uploaded file
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Convert to WAV if needed
        wav_path = convert_to_wav(file_path)

        try:
            # Transcribe the audio
            transcript = transcribe_audio(wav_path)

            # Translate the transcript
            translated_text = translate_text(transcript, target_lang)

            # Convert translated text to speech
            audio_path = text_to_speech(translated_text, target_lang)

            # Save the translated audio (copy file)
            output_path = os.path.join(app.config['UPLOAD_FOLDER'], f'translated_{filename}')
            with open(audio_path, 'rb') as src, open(output_path, 'wb') as dst:
                dst.write(src.read())

            # Return both the audio file and text content
            return jsonify({
                'original_text': transcript,
                'translated_text': translated_text,
                'audio_url': f'/download/{os.path.basename(output_path)}'
            })

        finally:
            # Clean up temporary files
            cleanup_temp_files([file_path, wav_path])

    except Exception as e:
        logger.error(f"Error in audio translation: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>')
def download_file(filename):
    try:
        return send_file(
            os.path.join(app.config['UPLOAD_FOLDER'], filename),
            as_attachment=True
        )
    except Exception as e:
        logger.error(f"Error downloading file: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/translate/video', methods=['POST'])
def translate_video():
    try:
        logger.debug("Starting video translation process")
        
        # Check if upload folder exists
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
            logger.debug(f"Created upload folder: {app.config['UPLOAD_FOLDER']}")
        
        if 'file' not in request.files:
            logger.error("No file in request.files")
            return jsonify({'error': 'No video file provided'}), 400
        
        video_file = request.files['file']
        logger.debug(f"Received file: {video_file.filename}")
        
        if video_file.filename == '':
            logger.error("Empty filename")
            return jsonify({'error': 'No selected file'}), 400
        
        # Validate file type
        allowed_extensions = {'mp4', 'avi', 'mov', 'webm'}
        if not video_file.filename.lower().endswith(tuple('.' + ext for ext in allowed_extensions)):
            logger.error(f"Invalid file type: {video_file.filename}")
            return jsonify({'error': 'Invalid file type. Please upload a video file.'}), 400
        
        # Save the uploaded video
        video_filename = secure_filename(video_file.filename)
        video_path = os.path.join(app.config['UPLOAD_FOLDER'], video_filename)
        logger.debug(f"Saving video to: {video_path}")
        video_file.save(video_path)
        
        # Verify video file exists and is not empty
        if not os.path.exists(video_path) or os.path.getsize(video_path) == 0:
            logger.error("Video file was not saved properly")
            return jsonify({'error': 'Failed to save video file'}), 500
        
        # Extract audio from video
        audio_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{os.path.splitext(video_filename)[0]}_audio.wav")
        logger.debug(f"Extracting audio to: {audio_path}")
        try:
            extract_audio_from_video(video_path, audio_path)
            if not os.path.exists(audio_path):
                raise Exception("Failed to extract audio from video")
        except Exception as e:
            logger.error(f"Error extracting audio: {str(e)}")
            return jsonify({'error': f'Failed to extract audio: {str(e)}'}), 500
        
        # Transcribe the audio
        logger.debug("Transcribing audio")
        try:
            transcript = transcribe_audio(audio_path)
            if not transcript:
                raise Exception("No transcript generated")
            logger.debug(f"Transcript: {transcript}")
        except Exception as e:
            logger.error(f"Error transcribing audio: {str(e)}")
            return jsonify({'error': f'Failed to transcribe audio: {str(e)}'}), 500
        
        # Translate the transcript
        logger.debug("Translating transcript")
        try:
            translated_text = translate_text(transcript)
            if not translated_text:
                raise Exception("No translation generated")
            logger.debug(f"Translated text: {translated_text}")
        except Exception as e:
            logger.error(f"Error translating text: {str(e)}")
            return jsonify({'error': f'Failed to translate text: {str(e)}'}), 500
        
        # Generate speech from translated text
        translated_audio_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{os.path.splitext(video_filename)[0]}_translated.mp3")
        logger.debug(f"Generating speech to: {translated_audio_path}")
        try:
            text_to_speech(translated_text, translated_audio_path)
            if not os.path.exists(translated_audio_path):
                raise Exception("Failed to generate translated audio")
        except Exception as e:
            logger.error(f"Error generating speech: {str(e)}")
            return jsonify({'error': f'Failed to generate translated audio: {str(e)}'}), 500
        
        # Apply lip-sync to the video
        output_video_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{os.path.splitext(video_filename)[0]}_translated.mp4")
        logger.debug(f"Applying lip-sync to: {output_video_path}")
        try:
            lip_synced_video_path = apply_lip_sync(video_path, translated_audio_path, output_video_path)
            if not os.path.exists(lip_synced_video_path):
                raise Exception("Failed to generate lip-synced video")
        except Exception as e:
            logger.error(f"Error applying lip-sync: {str(e)}")
            return jsonify({'error': f'Failed to apply lip-sync: {str(e)}'}), 500
        
        # Clean up temporary files
        try:
            logger.debug("Cleaning up temporary files")
            if os.path.exists(audio_path):
                os.remove(audio_path)
            if os.path.exists(translated_audio_path):
                os.remove(translated_audio_path)
            if os.path.exists(video_path):
                os.remove(video_path)
        except Exception as e:
            logger.warning(f"Error cleaning up temporary files: {str(e)}")
        
        # Return the results
        logger.debug("Returning results")
        return jsonify({
            'original_text': transcript,
            'translated_text': translated_text,
            'video_url': url_for('download_file', filename=os.path.basename(lip_synced_video_path))
        })
        
    except Exception as e:
        logger.error(f"Error in video translation: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({'error': 'File too large'}), 413

@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)