import cv2
import os
import subprocess

def _extract_frames(video_path, out_dir):
    """
    Internal function to extract frames using OpenCV.
    MODIFIED: Now samples frames based on time (seconds) rather than frame count.
    """
    print(f"Extracting frames from {os.path.basename(video_path)}...")
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open video file {video_path}")
        return 0, []

    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps == 0:
        print("Warning: Could not determine video FPS. Defaulting to 25.")
        fps = 25

    # --- NEW: Smarter Sampling Logic ---
    SECONDS_PER_SAMPLE = 2  # Extract one frame every 2 seconds
    frame_interval = int(fps * SECONDS_PER_SAMPLE)
    
    frame_count = 0
    sampled_files = []

    while True:
        frame_id = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
        ret, frame = cap.read()
        if not ret:
            break

        # Extract the very first frame, and then every 'frame_interval' frames
        if frame_id == 0 or frame_id % frame_interval == 0:
            frame_filename = os.path.join(out_dir, f"frame_{frame_count:04d}.jpg")
            cv2.imwrite(frame_filename, frame)
            sampled_files.append(frame_filename)
            frame_count += 1
    
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()
    print(f"Successfully extracted {frame_count} sampled frames (one every {SECONDS_PER_SAMPLE} seconds).")
    return total_frames, sampled_files

def _extract_audio(video_path, out_dir):
    """Internal function to extract audio using FFmpeg."""
    print(f"Extracting audio from {os.path.basename(video_path)}...")
    audio_path = os.path.join(out_dir, "audio.wav")
    
    # Use FFmpeg to extract audio. -y overwrites output, -vn disables video
    command = f"ffmpeg -i \"{video_path}\" -y -vn -acodec pcm_s16le -ar 16000 -ac 1 \"{audio_path}\""
    
    try:
        # Use DEVNULL to hide ffmpeg's verbose output unless there's an error
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        return audio_path
    except subprocess.CalledProcessError as e:
        # Check if the error is "does not contain any stream" which means no audio
        if "does not contain any stream" in e.stderr.decode():
            print("No audio track found in the video.")
        else:
            print(f"Error extracting audio with FFmpeg: {e.stderr.decode()}")
        return None

def preprocess_video(video_path, output_dir):
    """
    Main entry point for video processing. Orchestrates frame and audio extraction.
    """
    temp_dir = os.path.join(output_dir, "temp")
    frame_dir = os.path.join(temp_dir, "frames")
    os.makedirs(frame_dir, exist_ok=True)
    
    total_frames, sampled_frame_files = _extract_frames(video_path, frame_dir)
    audio_path = _extract_audio(video_path, temp_dir)
    
    return frame_dir, audio_path, total_frames, sampled_frame_files

