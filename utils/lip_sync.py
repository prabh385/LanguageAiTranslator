
import os
import logging
import subprocess
import tempfile
from lipsync import lip_sync

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def apply_lip_sync(video_path, audio_path, output_path):
    """
    Apply lip-sync using the lipsync library
    """
    try:
        logger.info(f"Applying lip-sync: video={video_path}, audio={audio_path}")

        # Ensure the output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Use the lipsync library
        lip_sync(video_path, audio_path, output_path)

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
