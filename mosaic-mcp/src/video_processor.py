"""
Video processing module.

- frame extraction
- audio transcription
- image captioning (caption the frames)
- Embedding Generation (generate embeddings for the captions, frames , transcripts)
- vector database storage (chromadb for text search and faiss for image search)
- complete video processing pipeline (process a video from start to finish)
- Video Summarization (generate a summary of the video content)

"""
# Import statements
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import subprocess
import tempfile
from pathlib import Path
from typing import List, Dict, Tuple
from groq import Groq
from PIL import Image
import numpy as np
from sentence_transformers import SentenceTransformer
import chromadb
import faiss
from dotenv import load_dotenv
import json
import re
import base64
import time
import torch

load_dotenv()

# Device configuration - Use GPU if available
DEVICE = os.getenv('DEVICE', 'auto')
if DEVICE == 'auto':
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
else:
    device = DEVICE

print(f"🚀 Using device: {device.upper()}")
if device == 'cuda':
    print(f"   GPU: {torch.cuda.get_device_name(0)}")
    print(f"   VRAM: {round(torch.cuda.get_device_properties(0).total_memory / 1024**3, 2)} GB")

# models with GPU support
clip_model = SentenceTransformer('clip-ViT-B-32', device=device)
text_model = SentenceTransformer('all-MiniLM-L6-v2', device=device)
groq_client = Groq(api_key=os.getenv('GROQ_API_KEY'))
N = 10  # take 1 in every 10th frame

# Vision model for image captioning (Groq supports llama-3.2-90b-vision-preview, meta-llama/llama-4-maverick-17b-128e-instruct
VISION_MODEL = os.getenv('VISION_MODEL', 'meta-llama/llama-4-maverick-17b-128e-instruct')
CAPTION_BATCH_SIZE = 5  # Process frames in batches to avoid rate limits
CAPTION_DELAY = 0.5  # Delay between API calls to avoid rate limiting


# Key frame extraction hybrid method (scene change + interval + keuyframe detection)

# os.makedirs(output_dir, exist_ok=True)
#     output_pattern = os.path.join(output_dir, "frame_%04d.jpg")

#     # ffmpeg filter: detect scene changes OR capture at fixed interval
#     # assumes ~30 fps for interval calculation
#     fps_guess = 30
#     interval_frames = interval_sec * fps_guess
#     vf_filter = f"select='gt(scene,{scene_thresh})+not(mod(n,{interval_frames}))'"

#     cmd = [
#         "ffmpeg",
#         "-i", video_path,
#         "-vf", vf_filter,
#         "-vsync", "vfr",
#         "-q:v", "2",
#         output_pattern
#     ]


# frame extraction
def extract_keyframes_ffmpeg(video_path: str, output_dir: str) -> Tuple[List[str], List[float]]:
    """
    Extract keyframes from a video using ffmpeg.
    extracting 1 in every 10 frames for simplicity.
    
    args:
        video_path: path to the input video file
        output_dir: directory to save the extracted frames
    returns:
        Tuple of (List of paths to the extracted frames, List of timestamps in seconds)
    """

    os.makedirs(output_dir, exist_ok=True)
    output_pattern = os.path.join(output_dir, 'frame_%04d.jpg')

    # First, get video FPS
    probe_cmd = [
        "ffprobe",
        "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=r_frame_rate",
        "-of", "csv=p=0",
        video_path
    ]
    
    try:
        fps_result = subprocess.run(probe_cmd, capture_output=True, text=True, check=True)
        fps_str = fps_result.stdout.strip()
        if '/' in fps_str:
            num, den = map(float, fps_str.split('/'))
            fps = num / den if den != 0 else 30.0
        else:
            fps = float(fps_str) if fps_str else 30.0
    except:
        fps = 30.0  # Default FPS

    cmd = [
        "ffmpeg",
        "-i", video_path,
        "-vf", "select='not(mod(n,10))'",
        "-vsync", "vfr",
        "-q:v", "2",
        output_pattern
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        error_msg = f"FFmpeg failed with return code {result.returncode}\nSTDERR: {result.stderr}\nSTDOUT: {result.stdout}"
        raise RuntimeError(error_msg)

    frames = sorted([
        os.path.join(output_dir, f)
        for f in os.listdir(output_dir)
        if f.endswith('.jpg')
    ])

    # Calculate timestamps: frame N corresponds to frame index N*10 in original video
    # timestamp = frame_index / fps
    timestamps = []
    for i in range(len(frames)):
        original_frame_index = i * N  # Every 10th frame
        timestamp = original_frame_index / fps
        timestamps.append(timestamp)

    return frames, timestamps

# extract audio 
def extract_audio_ffmpeg(video_path: str, output_path: str = None) -> str:
    if output_path is None:
        output_path = tempfile.mktemp(suffix=".wav")

    cmd = [
         "ffmpeg",
        "-i", video_path,
        "-ar", "16000",  # 16kHz sampling rate
        "-ac", "1",      # Mono channel
        "-map", "0:a",   # Audio stream only
        "-c:a", "pcm_s16le",  # WAV format
        "-y",            # Overwrite
        output_path
    ]

    subprocess.run(cmd, capture_output=True, check=True)
    return output_path

def split_audio_into_chunks(audio_path: str, chunk_duration_sec: int = 600) -> List[Tuple[str, float]]:
    """
    Split audio file into chunks of specified duration.
    
    Args:
        audio_path: Path to the input audio file
        chunk_duration_sec: Duration of each chunk in seconds (default 10 minutes)
    
    Returns:
        List of tuples (chunk_path, start_time_offset)
    """
    # Get audio duration
    probe_cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "csv=p=0",
        audio_path
    ]
    
    try:
        duration_result = subprocess.run(probe_cmd, capture_output=True, text=True, check=True)
        total_duration = float(duration_result.stdout.strip())
    except:
        # If we can't get duration, return original file
        return [(audio_path, 0.0)]
    
    # If file is small enough, return as-is
    if total_duration <= chunk_duration_sec:
        return [(audio_path, 0.0)]
    
    # Split into chunks
    chunks = []
    temp_dir = tempfile.mkdtemp()
    chunk_index = 0
    start_time = 0.0
    
    while start_time < total_duration:
        chunk_path = os.path.join(temp_dir, f"chunk_{chunk_index:04d}.wav")
        
        cmd = [
            "ffmpeg",
            "-i", audio_path,
            "-ss", str(start_time),
            "-t", str(chunk_duration_sec),
            "-ar", "16000",
            "-ac", "1",
            "-c:a", "pcm_s16le",
            "-y",
            chunk_path
        ]
        
        subprocess.run(cmd, capture_output=True, check=True)
        chunks.append((chunk_path, start_time))
        
        start_time += chunk_duration_sec
        chunk_index += 1
    
    return chunks

def transcribe_with_groq(audio_path: str, language: str = None) -> Dict:
    """
    Transcribe audio with Groq Whisper, automatically handling large files by chunking.
    
    Args:
        audio_path: Path to audio file
        language: Optional language code
    
    Returns:
        Dictionary with 'text' and 'segments' keys
    """
    # Check file size - if > 20MB, split into chunks (leaving buffer for safety)
    file_size_mb = os.path.getsize(audio_path) / (1024 * 1024)
    
    if file_size_mb > 20:
        print(f"Audio file is {file_size_mb:.1f}MB, splitting into chunks...")
        chunks = split_audio_into_chunks(audio_path, chunk_duration_sec=600)  # 10-minute chunks
        print(f"Split into {len(chunks)} chunks")
        
        all_text = []
        all_segments = []
        
        for i, (chunk_path, time_offset) in enumerate(chunks):
            print(f"Transcribing chunk {i+1}/{len(chunks)}...")
            
            try:
                with open(chunk_path, "rb") as audio_file:
                    transcription = groq_client.audio.transcriptions.create(
                        file=audio_file,
                        model="whisper-large-v3-turbo",
                        response_format="verbose_json",
                        timestamp_granularities=["word", "segment"],
                        language=language,
                        temperature=0.0
                    )
                
                all_text.append(transcription.text)
                
                # Adjust segment timestamps by chunk offset
                if hasattr(transcription, 'segments'):
                    for seg in transcription.segments:
                        all_segments.append({
                            "text": seg.get("text", ""),
                            "start": seg.get("start", 0) + time_offset,
                            "end": seg.get("end", 0) + time_offset
                        })
            
            finally:
                # Clean up chunk file
                try:
                    os.remove(chunk_path)
                except:
                    pass
        
        # Clean up temp directory
        try:
            os.rmdir(os.path.dirname(chunks[0][0]))
        except:
            pass
        
        return {
            "text": " ".join(all_text),
            "segments": all_segments
        }
    
    else:
        # File is small enough, transcribe directly
        with open(audio_path, "rb") as audio_file:
            transcription = groq_client.audio.transcriptions.create(
                file=audio_file,
                model="whisper-large-v3-turbo",
                response_format="verbose_json",
                timestamp_granularities=["word", "segment"],
                language=language,
                temperature=0.0
            )
        
        return {
            "text": transcription.text,
            "segments": [
                {
                    "text": seg.get("text", ""),
                    "start": seg.get("start", 0),
                    "end": seg.get("end", 0)
                }
                for seg in transcription.segments
            ] if hasattr(transcription, 'segments') else []
        }


# Embedding Function
def generate_image_embeddings(image_paths: List[str]) -> np.ndarray:
    """
    Generate CLIP embeddings for images.
    Batch processing for speed.
    """
    images = [Image.open(img_path).convert('RGB') for img_path in image_paths]
    embeddings = clip_model.encode(images, batch_size=32, show_progress_bar=False)
    return embeddings

def generate_text_embeddings(texts: List[str]) -> np.ndarray:
    """
    Generate embeddings for text using lightweight model.
    Fast and efficient for captions/transcripts.
    """
    embeddings = text_model.encode(texts, batch_size=32, show_progress_bar=False)
    return embeddings


# Vector DB Storage

def store_embeddings_faiss(embeddings: np.ndarray, index_path: str) -> faiss.Index:
    """
    Store image embeddings in FAISS index.
    Fast similarity search with GPU acceleration if available.
    """
    dimension = embeddings.shape[1]
    cpu_index = faiss.IndexFlatL2(dimension)
    cpu_index.add(embeddings.astype('float32'))
    
    # Try to use GPU for FAISS if available
    try:
        if device == 'cuda' and faiss.get_num_gpus() > 0:
            res = faiss.StandardGpuResources()
            gpu_index = faiss.index_cpu_to_gpu(res, 0, cpu_index)
            print("✓ FAISS using GPU acceleration")
            # Save CPU version to disk (GPU index can't be saved directly)
            faiss.write_index(cpu_index, index_path)
            return gpu_index
    except Exception as e:
        print(f"⚠ FAISS GPU not available ({e}), using CPU")
    
    # Save index to disk
    faiss.write_index(cpu_index, index_path)
    return cpu_index


def store_text_chromadb(
    texts: List[str], 
    embeddings: np.ndarray,
    metadatas: List[Dict],
    collection_name: str
) -> chromadb.Collection:
    """
    Store text embeddings and metadata in ChromaDB.
    """
    client = chromadb.PersistentClient(path="./chroma_db")
    
    # Delete existing collection if exists
    try:
        client.delete_collection(collection_name)
    except:
        pass
    
    collection = client.create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"}
    )
    
    ids = [f"doc_{i}" for i in range(len(texts))]
    
    collection.add(
        documents=texts,
        embeddings=embeddings.tolist(),
        metadatas=metadatas,
        ids=ids
    )
    
    return collection

# ===== Caption Generation =====

def encode_image_to_base64(image_path: str) -> str:
    """
    Encode an image file to base64 string for API calls.
    Resizes image if too large to reduce API payload.
    """
    with Image.open(image_path) as img:
        # Resize if image is too large (max 1024px on longest side)
        max_size = 1024
        if max(img.size) > max_size:
            ratio = max_size / max(img.size)
            new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
            img = img.resize(new_size, Image.Resampling.LANCZOS)
        
        # Convert to RGB if necessary
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Save to bytes
        import io
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=85)
        buffer.seek(0)
        return base64.b64encode(buffer.read()).decode('utf-8')


def caption_single_image(image_path: str, timestamp: float = None) -> str:
    """
    Generate a caption for a single image using Groq Vision model.
    
    Args:
        image_path: Path to the image file
        timestamp: Optional timestamp for context
        
    Returns:
        Caption string describing the image content
    """
    try:
        base64_image = encode_image_to_base64(image_path)
        
        time_context = f" at {timestamp:.1f} seconds" if timestamp else ""
        
        response = groq_client.chat.completions.create(
            model=VISION_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"Describe this video frame{time_context} in one concise sentence. Focus on: people, actions, objects, scene, text visible. Be specific and descriptive for search purposes."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=150,
            temperature=0.3
        )
        
        caption = response.choices[0].message.content.strip()
        return caption
        
    except Exception as e:
        print(f"Error captioning {image_path}: {e}")
        # Fallback to simple caption
        return f"Video frame at {timestamp:.1f}s" if timestamp else "Video frame"


def generate_captions_batch(image_paths: List[str], timestamps: List[float] = None) -> List[str]:
    """
    Generate captions for multiple images using Groq Vision model.
    Processes in batches with rate limiting to avoid API limits.
    
    Args:
        image_paths: List of paths to image files
        timestamps: Optional list of timestamps for each frame
        
    Returns:
        List of caption strings
    """
    captions = []
    total = len(image_paths)
    
    print(f"Generating captions for {total} frames using {VISION_MODEL}...")
    
    for i, image_path in enumerate(image_paths):
        timestamp = timestamps[i] if timestamps and i < len(timestamps) else None
        
        try:
            caption = caption_single_image(image_path, timestamp)
            captions.append(caption)
            
            if (i + 1) % 10 == 0:
                print(f"  Captioned {i + 1}/{total} frames")
            
            # Rate limiting delay
            if i < total - 1:
                time.sleep(CAPTION_DELAY)
                
        except Exception as e:
            print(f"Error captioning frame {i + 1}: {e}")
            fallback = f"Video frame {i + 1} at {timestamp:.1f}s" if timestamp else f"Video frame {i + 1}"
            captions.append(fallback)
    
    print(f"Completed captioning {len(captions)} frames")
    return captions


def generate_simple_captions(image_paths: List[str]) -> List[str]:
    """
    Generate simple captions based on frame numbers.
    Fallback for when vision model is unavailable.
    """
    captions = [f"Frame {i+1}" for i in range(len(image_paths))]
    return captions


class VideoProcessingPipeline():

    def __init__(self, storage_dir: str = "mosaic/extracted_frames"):
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)
        
        self.faiss_index = None
        self.chroma_collection = None
        self.frame_paths = []
    
    def process_video(self, video_path: str, video_id: str) -> Dict:
        # Create video-specific directories
        video_dir = os.path.join(self.storage_dir, video_id)
        frames_dir = os.path.join(video_dir, "frames")
        os.makedirs(frames_dir, exist_ok=True)
        
        print(f"Processing video: {video_path}")

    
        # Step 1: Extract keyframes using FFmpeg (now returns timestamps too)
        print("Extracting keyframes...")
        frame_paths, frame_timestamps = extract_keyframes_ffmpeg(video_path, frames_dir)
        self.frame_paths = frame_paths
        print(f"Extracted {len(frame_paths)} keyframes")
        
        # Save frame timestamps for later use in search
        timestamps_path = os.path.join(video_dir, "frame_timestamps.json")
        with open(timestamps_path, "w") as f:
            json.dump(frame_timestamps, f)
        print(f"Saved {len(frame_timestamps)} frame timestamps")
        
        # Save video path for clip generation
        video_info_path = os.path.join(video_dir, "video_info.json")
        with open(video_info_path, "w") as f:
            json.dump({
                "video_path": os.path.abspath(video_path),
                "video_id": video_id,
                "frame_count": len(frame_paths)
            }, f)

        #  Step 2: Extract and transcribe audio using Groq
        print("Extracting audio...")
        audio_path = os.path.join(video_dir, "audio.wav")
        extract_audio_ffmpeg(video_path, audio_path)

        print("Transcribing audio with Groq Whisper...")
        transcription_result = transcribe_with_groq(audio_path)
        transcript_text = transcription_result["text"]
        segments = transcription_result["segments"]
        print(f"Transcription complete: {len(transcript_text)} characters")


        # Step 3: Generate embeddings for frames
        print("Generating image embeddings...")
        image_embeddings = generate_image_embeddings(frame_paths)

        # Step 4: Store image embeddings in FAISS
        print("Storing image embeddings in FAISS...")
        faiss_index_path = os.path.join(video_dir, "faiss_index.bin")
        self.faiss_index = store_embeddings_faiss(image_embeddings, faiss_index_path)

        # Step 5: Store transcript in ChromaDB
        print("Storing transcript in ChromaDB...")
        
        # Store full transcript
        full_transcript_metadata = [{
            "type": "transcript",
            "video_id": video_id,
            "start": 0,
            "end": segments[-1]["end"] if segments else 0
        }]

        # Store transcript segments
        segment_texts = [seg["text"] for seg in segments]
        segment_embeddings = generate_text_embeddings([transcript_text] + segment_texts)
        
        segment_metadatas = [
            {
                "type": "transcript_segment",
                "video_id": video_id,
                "start": seg["start"],
                "end": seg["end"]
            }
            for seg in segments
        ]

        all_texts = [transcript_text] + segment_texts
        all_metadatas = full_transcript_metadata + segment_metadatas
        
        self.chroma_collection = store_text_chromadb(
            texts=all_texts,
            embeddings=segment_embeddings,
            metadatas=all_metadatas,
            collection_name=f"video_{video_id}"
        )

         # Step 6: Generate captions for frames using Vision model (only 1 in 10 frames)
        print("Generating AI captions for frames (1 in every 10)...")
        try:
            # Only caption every 10th frame to save API calls
            caption_interval = 10
            frames_to_caption = frame_paths[::caption_interval]
            timestamps_to_caption = frame_timestamps[::caption_interval]
            
            sparse_captions = generate_captions_batch(frames_to_caption, timestamps_to_caption)
            
            # Expand captions: assign each caption to the surrounding frames
            frame_captions = []
            caption_idx = 0
            for i in range(len(frame_paths)):
                # Find the nearest captioned frame
                nearest_caption_idx = min(i // caption_interval, len(sparse_captions) - 1)
                frame_captions.append(sparse_captions[nearest_caption_idx])
                
        except Exception as e:
            print(f"Vision captioning failed, using fallback: {e}")
            frame_captions = [f"Video frame {i+1} at {frame_timestamps[i]:.1f}s" for i in range(len(frame_paths))]
        
        # Save captions to file for reference
        captions_path = os.path.join(video_dir, "frame_captions.json")
        with open(captions_path, "w") as f:
            json.dump([
                {"frame_index": i, "timestamp": frame_timestamps[i], "caption": caption, "is_captioned": (i % 10 == 0)}
                for i, caption in enumerate(frame_captions)
            ], f, indent=2)
        
        # Step 7: Store frame captions in ChromaDB for semantic text search
        print("Storing frame captions in ChromaDB...")
        frame_caption_embeddings = generate_text_embeddings(frame_captions)
        frame_metadatas = [
            {
                "type": "frame",
                "video_id": video_id,
                "frame_path": frame_paths[i],
                "frame_index": i,
                "timestamp": frame_timestamps[i],
                "caption": frame_captions[i]
            }
            for i in range(len(frame_paths))
        ]

        store_text_chromadb(
            texts=frame_captions,
            embeddings=frame_caption_embeddings,
            metadatas=frame_metadatas,
            collection_name=f"frames_{video_id}"
        )



        print("Processing complete!")
        
        return {
            "status": "success",
            "video_id": video_id,
            "frames_extracted": len(frame_paths),
            "frames_captioned": len(frame_captions),
            "transcript_length": len(transcript_text),
            "segments_count": len(segments),
            "transcript": transcript_text,
            "faiss_index_path": faiss_index_path,
            "captions_path": captions_path,
            "vision_model_used": VISION_MODEL
        }
    

# pipeline = VideoProcessingPipeline(
#     storage_dir="mosaic/extracted_frames"
# )

# res = pipeline.process_video(
#     video_path="mosaic/my_video.mp4.webm",
#     video_id="video_001"
# )

# import pprint

# pprint.pprint(res)