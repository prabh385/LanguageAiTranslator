// Language selector functionality
document.getElementById('language-selector').addEventListener('change', function() {
    const selectedLanguage = this.options[this.selectedIndex].text;
    document.getElementById('target-language-label').textContent = selectedLanguage;
    document.getElementById('audio-target-language-label').textContent = selectedLanguage;
    document.getElementById('video-target-language-label').textContent = selectedLanguage;
});

// Text translation functionality - FIXED TO CALL REAL API
document.getElementById('translate-text-btn').addEventListener('click', async function() {
    const sourceText = document.getElementById('source-text').value;
    const targetLang = document.getElementById('language-selector').value;
    
    console.log("🔄 Translation button clicked");
    console.log("Text:", sourceText);
    console.log("Language:", targetLang);
    
    if (!sourceText.trim()) {
        showToast('Please enter some text to translate');
        return;
    }
    
    // Show loading state
    document.getElementById('translation-status').innerHTML = '<span class="text-primary"><i class="fas fa-spinner fa-spin me-1"></i>Translating...</span>';
    
    try {
        // Make API call to REAL backend
        const response = await fetch('/api/translate/text', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                text: sourceText,
                target_language: targetLang
            })
        });
        
        const data = await response.json();
        console.log("📦 API Response:", data);
        
        if (data.success) {
            document.getElementById('translation-status').innerHTML = '';
            document.getElementById('translated-text').textContent = data.translated_text;
            showToast('Text translated successfully!');
        } else {
            document.getElementById('translation-status').innerHTML = '<span class="text-danger">Translation failed</span>';
            showToast('Translation failed: ' + (data.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('❌ API Error:', error);
        document.getElementById('translation-status').innerHTML = '<span class="text-danger">Network error</span>';
        showToast('Network error occurred');
    }
});

// Clear text functionality
document.getElementById('clear-text-btn').addEventListener('click', function() {
    document.getElementById('source-text').value = '';
    document.getElementById('translated-text').textContent = '';
    document.getElementById('translation-status').innerHTML = '<span class="text-muted">Translation will appear here</span>';
});

// Copy translation functionality
document.getElementById('copy-translation-btn').addEventListener('click', function() {
    const translatedText = document.getElementById('translated-text').textContent;
    if (!translatedText.trim()) {
        showToast('No translation to copy');
        return;
    }
    
    navigator.clipboard.writeText(translatedText)
        .then(() => showToast('Translation copied to clipboard!'))
        .catch(() => showToast('Failed to copy translation'));
});

// Audio file upload functionality
const audioDropZone = document.getElementById('audio-drop-zone');
const audioFileInput = document.getElementById('audio-file');

audioDropZone.addEventListener('click', () => audioFileInput.click());
audioDropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    audioDropZone.classList.add('glow');
});
audioDropZone.addEventListener('dragleave', () => {
    audioDropZone.classList.remove('glow');
});
audioDropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    audioDropZone.classList.remove('glow');
    if (e.dataTransfer.files.length) {
        audioFileInput.files = e.dataTransfer.files;
        handleAudioFileSelect();
    }
});

audioFileInput.addEventListener('change', handleAudioFileSelect);

function handleAudioFileSelect() {
    if (audioFileInput.files.length) {
        const file = audioFileInput.files[0];
        const previewContainer = document.getElementById('audio-preview-container');
        const preview = document.getElementById('audio-preview');
        
        preview.src = URL.createObjectURL(file);
        previewContainer.style.display = 'block';
        
        // Enhanced file info display
        const fileSize = (file.size / (1024 * 1024)).toFixed(2);
        const fileType = file.type.split('/')[1]?.toUpperCase() || 'AUDIO';
        
        audioDropZone.innerHTML = `
            <i class="fas fa-check-circle text-success fa-2x mb-2"></i>
            <h5 class="mb-1">${file.name}</h5>
            <p class="text-muted mb-1">${fileSize} MB • ${fileType}</p>
            <small class="text-info">Ready for translation</small>
        `;
        
        audioDropZone.classList.add('bg-light');
    }
}

// Audio translation form submission - FIXED TO CALL REAL API
// Audio translation form submission
document.getElementById('audio-upload-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    if (!audioFileInput.files.length) {
        showToast('Please select an audio file');
        return;
    }
    
    document.getElementById('audio-translation-placeholder').style.display = 'none';
    document.getElementById('audio-processing').style.display = 'block';
    document.getElementById('audio-results').style.display = 'none';
    
    const targetLang = document.getElementById('language-selector').value;
    const formData = new FormData();
    formData.append('file', audioFileInput.files[0]);
    formData.append('target_language', targetLang);
    
    try {
        const response = await fetch('/api/translate/audio', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        // In the audio translation success handler:
if (data.success) {
    document.getElementById('audio-processing').style.display = 'none';
    document.getElementById('audio-results').style.display = 'block';
    
    document.getElementById('audio-original-text').textContent = data.original_text;
    document.getElementById('audio-translated-text').textContent = data.translated_text;
    
    // Show translated audio player
    const translatedAudioContainer = document.getElementById('translated-audio-container');
    const translatedAudio = document.getElementById('translated-audio');
    translatedAudio.src = data.audio_url;
    translatedAudioContainer.style.display = 'block';
    
    // Show Punjabi warning if present
    if (data.warning) {
        showToast(data.warning, 'warning'); // Show as warning toast
        // You could also show it in the UI
        const warningElement = document.createElement('div');
        warningElement.className = 'alert alert-warning mt-3';
        warningElement.innerHTML = `<i class="fas fa-exclamation-triangle me-2"></i>${data.warning}`;
        document.getElementById('audio-results').prepend(warningElement);
    } else {
        showToast('Audio translation completed!');
    }

        } else {
            document.getElementById('audio-processing').style.display = 'none';
            document.getElementById('audio-translation-placeholder').style.display = 'block';
            showToast('Audio translation failed: ' + (data.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('❌ Audio API Error:', error);
        document.getElementById('audio-processing').style.display = 'none';
        document.getElementById('audio-translation-placeholder').style.display = 'block';
        showToast('Audio translation failed: Network error');
    }
});
// Video file upload functionality
const videoDropZone = document.getElementById('video-drop-zone');
const videoFileInput = document.getElementById('video-file');

videoDropZone.addEventListener('click', () => videoFileInput.click());
videoDropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    videoDropZone.classList.add('glow');
});
videoDropZone.addEventListener('dragleave', () => {
    videoDropZone.classList.remove('glow');
});
videoDropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    videoDropZone.classList.remove('glow');
    if (e.dataTransfer.files.length) {
        videoFileInput.files = e.dataTransfer.files;
        handleVideoFileSelect();
    }
});

videoFileInput.addEventListener('change', handleVideoFileSelect);

function handleVideoFileSelect() {
    if (videoFileInput.files.length) {
        const file = videoFileInput.files[0];
        const previewContainer = document.getElementById('video-preview-container');
        const preview = document.getElementById('video-preview');
        const placeholder = document.getElementById('video-placeholder');
        
        preview.src = URL.createObjectURL(file);
        previewContainer.style.display = 'block';
        placeholder.style.display = 'none';
        
        videoDropZone.innerHTML = `
            <i class="fas fa-check-circle text-success"></i>
            <h5>${file.name}</h5>
            <p class="text-muted">${(file.size / (1024 * 1024)).toFixed(2)} MB</p>
        `;
    }
}

// Video translation form submission - FIXED TO CALL REAL API
document.getElementById('video-translation-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    if (!videoFileInput.files.length) {
        showToast('Please select a video file');
        return;
    }
    
    document.getElementById('video-processing-message').style.display = 'block';
    document.getElementById('translated-video-container').style.display = 'none';
    
    const targetLang = document.getElementById('language-selector').value;
    const formData = new FormData();
    formData.append('file', videoFileInput.files[0]);
    formData.append('target_language', targetLang);
    
    try {
        const response = await fetch('/api/translate/video', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            document.getElementById('video-processing-message').style.display = 'none';
            document.getElementById('translated-video-container').style.display = 'block';
            
            document.getElementById('video-original-text').textContent = data.original_text;
            document.getElementById('video-translated-text').textContent = data.translated_text;
            
            // Show translated video player
            const translatedVideo = document.getElementById('translated-video');
            translatedVideo.src = data.video_url;
            
            showToast('Video translation completed!');
        } else {
            showToast('Video translation failed: ' + data.error);
        }
    } catch (error) {
        console.error('❌ Video API Error:', error);
        showToast('Video translation failed');
    }
});

// Download video button
document.getElementById('download-video-btn').addEventListener('click', function() {
    showToast('Downloading translated video...');
});

// Toast notification function
function showToast(message) {
    const toastElement = document.getElementById('toast-notification');
    const toastBody = toastElement.querySelector('.toast-body');
    toastBody.textContent = message;
    
    const toast = new bootstrap.Toast(toastElement);
    toast.show();
}

// Add some interactive effects to cards
document.querySelectorAll('.card').forEach(card => {
    card.addEventListener('mouseenter', function() {
        this.style.transform = 'translateY(-10px) rotateX(5deg)';
    });
    
    card.addEventListener('mouseleave', function() {
        this.style.transform = 'translateY(0) rotateX(0)';
    });
});

// Character counter for text area
document.getElementById('source-text').addEventListener('input', function() {
    const charCount = this.value.length;
    const counter = document.getElementById('char-counter') || createCharCounter();
    counter.textContent = `${charCount} characters`;
    
    if (charCount > 1000) {
        counter.classList.add('warning');
    } else {
        counter.classList.remove('warning');
    }
    
    if (charCount > 2000) {
        counter.classList.add('danger');
    } else {
        counter.classList.remove('danger');
    }
});

function createCharCounter() {
    const counter = document.createElement('div');
    counter.id = 'char-counter';
    counter.className = 'char-counter';
    document.getElementById('source-text').parentNode.appendChild(counter);
    return counter;
}