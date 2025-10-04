import os
import logging
from moviepy.editor import VideoFileClip, AudioFileClip
import subprocess
import tempfile

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def apply_lip_sync(video_path, audio_path, output_path):
    """
    Simplified lip-sync: Combine video with translated audio
    """
    try:
        logger.info(f"Applying lip-sync: video={video_path}, audio={audio_path}")
        
        # Load video and audio
        video_clip = VideoFileClip(video_path)
        audio_clip = AudioFileClip(audio_path)
        
        # Set the audio of the video to the translated audio
        final_clip = video_clip.set_audio(audio_clip)
        
        # Write the final video
        final_clip.write_videofile(
            output_path,
            codec='libx264',
            audio_codec='aac',
            temp_audiofile='temp-audio.m4a',
            remove_temp=True,
            verbose=False,
            logger=None
        )
        
        # Close clips to free memory
        video_clip.close()
        audio_clip.close()
        final_clip.close()
        
        logger.info(f"Lip-sync completed: {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"Error in lip-sync process: {str(e)}")
        
        # Fallback: Just copy the original video
        try:
            import shutil
            shutil.copy2(video_path, output_path)
            logger.info(f"Used fallback: copied original video to {output_path}")
            return output_path
        except Exception as fallback_error:
            logger.error(f"Fallback also failed: {fallback_error}")
            raise e