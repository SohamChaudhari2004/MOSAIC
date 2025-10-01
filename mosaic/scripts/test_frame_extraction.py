import subprocess
import os
from typing import List


def extract_keyframes_ffmpeg(video_path: str, output_dir: str) -> List[str]:
    """
    Extract I-frames (keyframes) from video using FFmpeg.
    Fast and efficient - only extracts actual keyframes.
    """
    os.makedirs(output_dir, exist_ok=True)
    output_pattern = os.path.join(output_dir, "frame_%04d.jpg")
    
    # Extract only I-frames (keyframes) for speed
    # cmd = [
    #     "ffmpeg",
    #     "-skip_frame", "nokey",
    #      video_path,
    #     "-vsync", "vfr",
    #     "-frame_pts", "true",
    #     "-q:v", "2",  # High quality JPEG
    #     output_pattern
    # ]
    
#     cmd = [
#     "ffmpeg",
#     "-i", video_path,      # input video
#     "-vsync", "vfr",       # variable frame rate handling
#     "-q:v", "2",           # high-quality JPEG
#     output_pattern
# ]

#     cmd = [
#     "ffmpeg",
#     "-i", video_path,
#     "-vf", "select='gt(scene,0.3)'",
#     "-vsync", "vfr",
#     "-q:v", "2",
#     output_pattern
# ]
    # fps = 1  # 1 frame per second
    # cmd = [
    #     "ffmpeg",
    #     "-i", video_path,
    #     "-vf", f"fps={fps}",
    #     "-q:v", "2",
    #     output_pattern
    # ]
    N = 10  # take every 10th frame
    cmd = [
        "ffmpeg",
        "-i", video_path,
        "-vf", f"select='not(mod(n\,{N}))'",
        "-vsync", "vfr",
        "-q:v", "2",
        output_pattern
    ]

    subprocess.run(cmd, capture_output=True, check=True)
    
    # Get all extracted frames
    frames = sorted([
        os.path.join(output_dir, f) 
        for f in os.listdir(output_dir) 
        if f.endswith('.jpg')
    ])
    
    return frames

extract_keyframes_ffmpeg(
    "mosaic/nana_welcome.mp4",
    "mosaic/extracted_frames"
)
