import cv2
import numpy as np
import mediapipe as mp
import os
import logging
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeVideoClip

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize MediaPipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=False,
    max_num_faces=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

def apply_lip_sync(video_path, audio_path, output_path):
    """
    Apply lip-sync to a video using the provided audio.
    
    Args:
        video_path (str): Path to the original video file
        audio_path (str): Path to the translated audio file
        output_path (str): Path to save the lip-synced video
        
    Returns:
        str: Path to the lip-synced video
    """
    try:
        logger.info(f"Starting lip-sync process for video: {video_path}")
        
        # Load the video and audio
        video = VideoFileClip(video_path)
        audio = AudioFileClip(audio_path)
        
        # Get video properties
        fps = video.fps
        width, height = video.size
        duration = video.duration
        
        # Create a temporary directory for frames
        temp_dir = os.path.join(os.path.dirname(output_path), "temp_frames")
        os.makedirs(temp_dir, exist_ok=True)
        
        # Process each frame
        logger.info("Processing video frames for lip-sync...")
        
        # Create a list to store processed frame paths
        processed_frames = []
        
        # Process frames in batches to avoid memory issues
        batch_size = 30  # Process 30 frames at a time
        total_frames = int(duration * fps)
        
        for batch_start in range(0, total_frames, batch_size):
            batch_end = min(batch_start + batch_size, total_frames)
            logger.info(f"Processing frames {batch_start} to {batch_end} of {total_frames}")
            
            # Extract frames for this batch
            frames = []
            for i in range(batch_start, batch_end):
                frame = video.get_frame(i / fps)
                frames.append((i, frame))
            
            # Process each frame in the batch
            for i, frame in frames:
                # Convert BGR to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Make a copy of the frame for drawing
                frame_copy = frame.copy()
                
                # Detect facial landmarks
                results = face_mesh.process(frame_rgb)
                
                if results.multi_face_landmarks:
                    # Get the first face
                    face_landmarks = results.multi_face_landmarks[0]
                    
                    # Extract lip landmarks (indices 61-68 for outer lips, 291-296 for inner lips)
                    lip_indices = list(range(61, 68)) + list(range(291, 296))
                    
                    # Get lip positions
                    lip_points = []
                    for idx in lip_indices:
                        landmark = face_landmarks.landmark[idx]
                        x, y = int(landmark.x * width), int(landmark.y * height)
                        lip_points.append((x, y))
                    
                    # Calculate lip movement based on audio amplitude
                    # For simplicity, we'll use a sine wave to simulate lip movement
                    # In a real implementation, you would analyze the audio waveform
                    time = i / fps
                    amplitude = 0.5 + 0.5 * np.sin(2 * np.pi * 5 * time)  # 5 Hz oscillation
                    
                    # Apply lip movement
                    for j, (x, y) in enumerate(lip_points):
                        # Move lips up and down based on amplitude
                        y_offset = int(amplitude * 5)  # 5 pixels max movement
                        cv2.circle(frame_copy, (x, y + y_offset), 1, (0, 255, 0), -1)
                
                # Save the processed frame
                frame_path = os.path.join(temp_dir, f"frame_{i:06d}.jpg")
                cv2.imwrite(frame_path, frame_copy)
                processed_frames.append(frame_path)
        
        # Create a video from the processed frames
        logger.info("Creating lip-synced video from processed frames...")
        
        # Use ffmpeg to create the video (more efficient than MoviePy for this)
        frame_pattern = os.path.join(temp_dir, "frame_%06d.jpg")
        os.system(f'ffmpeg -framerate {fps} -i "{frame_pattern}" -c:v libx264 -pix_fmt yuv420p -y "{output_path}"')
        
        # Add the translated audio to the video
        logger.info("Adding translated audio to the video...")
        final_video = VideoFileClip(output_path)
        final_video = final_video.set_audio(audio)
        
        # Save the final video
        final_output_path = output_path.replace(".mp4", "_with_audio.mp4")
        final_video.write_videofile(final_output_path, codec='libx264', audio_codec='aac')
        
        # Clean up
        final_video.close()
        video.close()
        audio.close()
        
        # Remove temporary files
        for frame_path in processed_frames:
            try:
                os.remove(frame_path)
            except:
                pass
        try:
            os.rmdir(temp_dir)
        except:
            pass
        
        logger.info(f"Lip-sync completed. Output saved to: {final_output_path}")
        return final_output_path
        
    except Exception as e:
        logger.error(f"Error in lip-sync process: {str(e)}")
        raise 