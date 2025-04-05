// Main application JavaScript for AI Multimodal Translation

// Helper function to convert base64 to Blob with improved error handling
function base64toBlob(base64Data, contentType) {
    try {
        // Add proper error handling
        if (!base64Data) {
            console.error("No base64 data provided to base64toBlob");
            throw new Error("Missing base64 data");
        }
        
        // Remove potential data URI prefix (e.g., "data:audio/wav;base64,")
        let base64String = base64Data;
        if (base64String.includes(',')) {
            base64String = base64String.split(',')[1];
        }
        
        // Set default content type if not provided
        contentType = contentType || '';
        
        // Log the content type and length for debugging
        console.log(`Converting base64 to blob - Content type: ${contentType}, Length: ${base64String.length}`);
        
        // Create a more efficient conversion with better error handling
        const sliceSize = 1024;
        let byteCharacters;
        
        try {
            byteCharacters = atob(base64String);
        } catch (e) {
            console.error("Failed to decode base64 data:", e);
            throw new Error("Invalid base64 data - could not decode");
        }
        
        const bytesLength = byteCharacters.length;
        const slicesCount = Math.ceil(bytesLength / sliceSize);
        const byteArrays = new Array(slicesCount);
        
        console.log(`Base64 decoded to ${bytesLength} bytes, creating ${slicesCount} slices`);

        // Process in slices to avoid memory issues with large files
        for (let sliceIndex = 0; sliceIndex < slicesCount; ++sliceIndex) {
            const begin = sliceIndex * sliceSize;
            const end = Math.min(begin + sliceSize, bytesLength);
            
            // Create typed array directly instead of using intermediate array
            const bytes = new Uint8Array(end - begin);
            for (let offset = begin, i = 0; offset < end; ++i, ++offset) {
                bytes[i] = byteCharacters.charCodeAt(offset);
            }
            byteArrays[sliceIndex] = bytes;
        }
        
        // Create and return the blob
        const blob = new Blob(byteArrays, { type: contentType });
        console.log(`Successfully created blob of size: ${blob.size} bytes`);
        return blob;
    } catch (error) {
        console.error("Error in base64toBlob:", error);
        throw error;
    }
}

document.addEventListener('DOMContentLoaded', function() {
    // Initialize components
    initializeLanguageSelector();
    initializeTextTranslation();
    initializeAudioTranslation();
    initializeVideoTranslation();
    initializeClipboard();
    
    // Setup tab switching behavior
    document.querySelectorAll('.nav-link').forEach(tab => {
        tab.addEventListener('click', function() {
            document.querySelectorAll('.nav-link').forEach(t => t.classList.remove('active'));
            this.classList.add('active');
        });
    });
});

// Initialize language selector
function initializeLanguageSelector() {
    const languageSelector = document.getElementById('language-selector');
    const targetLanguageLabels = [
        document.getElementById('target-language-label'),
        document.getElementById('audio-target-language-label'),
        document.getElementById('video-target-language-label')
    ];
    
    languageSelector.addEventListener('change', function() {
        const selectedLanguage = this.options[this.selectedIndex].text;
        // Update all language labels
        targetLanguageLabels.forEach(label => {
            if (label) label.textContent = selectedLanguage;
        });
    });
}

// Text Translation Functions
function initializeTextTranslation() {
    const translateButton = document.getElementById('translate-text-btn');
    const clearButton = document.getElementById('clear-text-btn');
    const sourceText = document.getElementById('source-text');
    const translatedText = document.getElementById('translated-text');
    const translationStatus = document.getElementById('translation-status');
    
    // Translate button click handler
    translateButton.addEventListener('click', function() {
        const text = sourceText.value.trim();
        if (!text) {
            showToast('Please enter some text to translate', 'warning');
            return;
        }
        
        const language = document.getElementById('language-selector').value;
        translationStatus.innerHTML = '<div class="spinner-border spinner-border-sm text-light" role="status"><span class="visually-hidden">Loading...</span></div> Translating...';
        
        // Clear previous content
        translatedText.textContent = '';
        
        // Make API request to translate text
        fetch('/translate/text', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                text: text,
                target_lang: language
            })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            console.debug('Translation response:', data);
            if (data.error) {
                throw new Error(data.error);
            }
            console.debug('Setting translated text:', data.translated_text);
            
            // Create a new div to hold the content
            const contentDiv = document.createElement('div');
            contentDiv.textContent = data.translated_text;
            
            // Clear and then append the new content
            translatedText.innerHTML = '';
            translatedText.appendChild(contentDiv);
            
            translationStatus.innerHTML = '<span class="text-success"><i class="fas fa-check-circle me-1"></i>Translation complete</span>';
        })
        .catch(error => {
            console.error('Translation Error:', error);
            console.debug('Error details:', error.message, error.stack);
            translatedText.textContent = '';
            translationStatus.innerHTML = `<span class="text-danger"><i class="fas fa-exclamation-circle me-1"></i>${error.message || 'Translation failed'}</span>`;
            showToast(error.message || 'Translation failed', 'danger');
        });
    });
    
    // Clear button click handler
    clearButton.addEventListener('click', function() {
        sourceText.value = '';
        translatedText.textContent = '';
        translationStatus.innerHTML = '<span class="text-muted">Translation will appear here</span>';
    });
}

// Audio Translation Functions
function initializeAudioTranslation() {
    const audioForm = document.getElementById('audio-upload-form');
    const audioFile = document.getElementById('audio-file');
    const audioPreviewContainer = document.getElementById('audio-preview-container');
    const audioPreview = document.getElementById('audio-preview');
    const audioResults = document.getElementById('audio-results');
    const audioPlaceholder = document.getElementById('audio-translation-placeholder');
    const audioProcessing = document.getElementById('audio-processing');
    const audioOriginalText = document.getElementById('audio-original-text');
    const audioTranslatedText = document.getElementById('audio-translated-text');
    const translatedAudioContainer = document.getElementById('translated-audio-container');
    const translatedAudio = document.getElementById('translated-audio');
    
    // Audio file change handler - preview
    audioFile.addEventListener('change', function() {
        if (this.files && this.files[0]) {
            const file = this.files[0];
            
            // Check file type
            if (!file.type.match('audio.*')) {
                showToast('Please select an audio file (MP3, WAV, OGG)', 'warning');
                this.value = '';
                audioPreviewContainer.style.display = 'none';
                return;
            }
            
            // Check file size (max 16MB)
            if (file.size > 16 * 1024 * 1024) {
                showToast('File size exceeds 16MB limit', 'warning');
                this.value = '';
                audioPreviewContainer.style.display = 'none';
                return;
            }
            
            const url = URL.createObjectURL(file);
            audioPreview.src = url;
            audioPreviewContainer.style.display = 'block';
        }
    });
    
    // Form submit handler
    audioForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const file = audioFile.files[0];
        if (!file) {
            showToast('Please select an audio file', 'warning');
            return;
        }
        
        const language = document.getElementById('language-selector').value;
        const formData = new FormData();
        formData.append('file', file);
        formData.append('target_lang', language);
        
        // Show processing indicator
        audioPlaceholder.style.display = 'none';
        audioProcessing.style.display = 'block';
        audioResults.style.display = 'none';
        
        // Make API request to translate audio
        fetch('/translate/audio', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (data.error) {
                throw new Error(data.error);
            }
            
            // Display original and translated text
            audioOriginalText.textContent = data.original_text;
            audioTranslatedText.textContent = data.translated_text;
            
            // Load and play the translated audio
            fetch(data.audio_url)
                .then(response => response.blob())
                .then(blob => {
                    const url = URL.createObjectURL(blob);
                    translatedAudio.src = url;
                    translatedAudioContainer.style.display = 'block';
                })
                .catch(error => {
                    console.error('Error loading audio:', error);
                    showToast('Error loading translated audio', 'warning');
                });
            
            // Show results
            audioProcessing.style.display = 'none';
            audioResults.style.display = 'block';
        })
        .catch(error => {
            console.error('Audio Translation Error:', error);
            audioProcessing.style.display = 'none';
            audioPlaceholder.style.display = 'block';
            showToast(error.message || 'Audio translation failed', 'danger');
        });
    });
}

// Video Translation Functions
function initializeVideoTranslation() {
    const videoForm = document.getElementById('video-translation-form');
    const videoPreview = document.getElementById('video-preview');
    const videoFileInput = document.getElementById('video-file');
    const translatedVideoContainer = document.getElementById('translated-video-container');
    const translatedVideo = document.getElementById('translated-video');
    const videoProcessingMessage = document.getElementById('video-processing-message');
    const videoOriginalText = document.getElementById('video-original-text');
    const videoTranslatedText = document.getElementById('video-translated-text');
    const downloadVideoBtn = document.getElementById('download-video-btn');
    
    videoFileInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            // Validate file type
            const allowedTypes = ['video/mp4', 'video/avi', 'video/quicktime', 'video/webm'];
            if (!allowedTypes.includes(file.type)) {
                showToast('Please upload a valid video file (MP4, AVI, MOV, or WEBM)', 'error');
                this.value = '';
                return;
            }
            
            // Validate file size (100MB limit)
            if (file.size > 100 * 1024 * 1024) {
                showToast('Video file size must be less than 100MB', 'error');
                this.value = '';
                return;
            }
            
            // Show video preview
            videoPreview.src = URL.createObjectURL(file);
            videoPreview.style.display = 'block';
            document.getElementById('video-preview-container').style.display = 'block';
        }
    });
    
    videoForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const formData = new FormData();
        const videoFile = videoFileInput.files[0];
        
        if (!videoFile) {
            showToast('Please select a video file', 'error');
            return;
        }
        
        formData.append('file', videoFile);
        
        try {
            // Show processing message
            videoProcessingMessage.style.display = 'block';
            videoProcessingMessage.textContent = 'Processing video... This may take a few minutes.';
            
            // Disable form
            videoForm.querySelectorAll('input, button').forEach(el => el.disabled = true);
            
            // Send request
            const response = await fetch('/translate/video', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            
            const data = await response.json();
            
            // Display original and translated text
            videoOriginalText.textContent = data.original_text || "No text available";
            videoTranslatedText.textContent = data.translated_text || "No translation available";
            
            // Display translated video
            translatedVideo.src = data.video_url;
            translatedVideoContainer.style.display = 'block';
            
            // Setup download button
            downloadVideoBtn.onclick = function() {
                const a = document.createElement('a');
                a.href = data.video_url;
                a.download = `translated_${videoFile.name}`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
            };
            
            // Hide processing message
            videoProcessingMessage.style.display = 'none';
            
            showToast('Video translation completed successfully!', 'success');
            
        } catch (error) {
            console.error('Error:', error);
            showToast('Error translating video: ' + error.message, 'error');
            videoProcessingMessage.style.display = 'none';
        } finally {
            // Re-enable form
            videoForm.querySelectorAll('input, button').forEach(el => el.disabled = false);
        }
    });

    // Add event listener for video loading error
    translatedVideo.addEventListener('error', function() {
        showToast('Error loading translated video', 'error');
        videoProcessingMessage.style.display = 'none';
    });
}

// Clipboard functionality
function initializeClipboard() {
    const copyBtn = document.getElementById('copy-translation-btn');
    const translatedText = document.getElementById('translated-text');
    
    copyBtn.addEventListener('click', function() {
        if (!translatedText.textContent.trim()) {
            showToast('No translation to copy', 'warning');
            return;
        }
        
        navigator.clipboard.writeText(translatedText.textContent.trim())
            .then(() => {
                showToast('Translation copied to clipboard', 'success');
            })
            .catch(err => {
                console.error('Could not copy text: ', err);
                showToast('Failed to copy to clipboard', 'danger');
            });
    });
}

// Toast notification function
function showToast(message, type = 'info') {
    const toast = document.getElementById('toast-notification');
    const toastBody = toast.querySelector('.toast-body');
    
    // Set message
    toastBody.textContent = message;
    
    // Set background color based on type
    toast.className = 'toast align-items-center text-white border-0';
    switch(type) {
        case 'success':
            toast.classList.add('bg-success');
            break;
        case 'warning':
            toast.classList.add('bg-warning');
            break;
        case 'danger':
            toast.classList.add('bg-danger');
            break;
        default:
            toast.classList.add('bg-primary');
    }
    
    // Initialize and show toast
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
}