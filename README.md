# AI Multimodal Translation Application

A Flask-based web application that provides multimodal translation capabilities including text, audio, and video translation with lip-sync support.

## Features

- **Text Translation**: Translate text between multiple languages
- **Audio Translation**: Convert speech to text, translate, and generate translated audio
- **Video Translation**: 
  - Extract audio from video
  - Transcribe speech to text
  - Translate the text
  - Generate translated audio
  - Apply lip-sync to the video
  - Generate final translated video

## Supported Languages

- Hindi 
- Tamil 
- Telugu 
- Malayalam 
- Bengali 
- Marathi 
- Gujarati
- Kannada
- Punjabi 

## Prerequisites

- **Recommended Python version: 3.11**  
  (Some dependencies may not work with Python 3.12 or newer)
- FFmpeg (for video processing)
- Internet connection (for speech recognition and translation services)

## Installation

1. Clone the repository:
```bash
git clone <https://github.com/prabh385/LanguageAiTranslator.git>
cd LanguageAiTranslator
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On Unix or MacOS
source venv/bin/activate
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

## Project Structure

```
LanguageAiTranslator/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── static/
│   ├── css/             # CSS styles
│   └── js/              # JavaScript files
├── templates/           # HTML templates
└── utils/
    ├── audio_video_utils.py  # Audio and video processing utilities
    ├── fixed_translation.py  # Text translation utilities
    └── lip_sync.py          # Lip-sync implementation
```

## Usage

1. Start the Flask application:
```bash
python app.py
```

2. Open your web browser and navigate to `http://localhost:5000`

3. Use the application:

   ### Text Translation
   - Enter text in the source language
   - Select target language
   - Click "Translate"
   - View translated text
   - Use "Copy to Clipboard" to copy the translation

   ### Audio Translation
   - Upload an audio file (MP3, WAV, OGG)
   - Select target language
   - Click "Translate Audio"
   - View original and translated text
   - Play the translated audio
   - Download the translated audio file

   ### Video Translation
   - Upload a video file (MP4, AVI, MOV, WEBM)
   - Select target language
   - Click "Translate Video"
   - View original and translated text
   - Watch the translated video with lip-sync
   - Download the translated video

## Technical Details

### Text Translation
- Uses Google Translate API for text translation
- Supports multiple Indian languages
- Includes error handling and retry mechanisms

### Audio Processing
- Extracts audio from video files using MoviePy
- Converts audio to WAV format for processing
- Uses Google Speech Recognition for transcription
- Generates translated audio using gTTS

### Video Processing
- Extracts audio from video files
- Applies lip-sync using MediaPipe Face Mesh
- Generates final video with translated audio
- Supports various video formats

## Error Handling

The application includes comprehensive error handling for:
- Network connectivity issues
- File format validation
- File size limits
- Speech recognition failures
- Translation service errors
- Video processing errors

## Limitations

- Maximum file size: 100MB for videos, 16MB for audio
- Supported video formats: MP4, AVI, MOV, WEBM
- Supported audio formats: MP3, WAV, OGG
- Requires internet connection for translation services
- Lip-sync quality depends on video quality and face visibility

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Google Translate API for translation services
- Google Speech Recognition for audio transcription
- MediaPipe for face mesh and lip-sync
- MoviePy for video processing
- Flask for the web framework
