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
from concurrent.futures import ThreadPoolExecutor
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

load_dotenv()

# models 
clip_model = SentenceTransformer('clip-ViT-B-32')
text_model = SentenceTransformer('all-MiniLM-L6-v2')
groq_client = Groq(api_key=os.getenv('GROQ_API_KEY'))
N = 10  # take 1 in every 10th frame


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
def extract_keyframes_ffmpeg(video_path: str, output_dir: str) -> List[str]:
    """
    Extract keyframes from a video using ffmpeg.
    extracting 1 in every 10 seconds for simplicity.
    
    args:
        video_path: path to the input video file
        output_dir: directory to save the extracted frames
    returns:
        List of paths to the extracted frames
    """

    os.makedirs(output_dir, exist_ok=True)
    output_pattern = os.path.join(output_dir, 'frame_%04d.jpg')

    cmd = [
        "ffmpeg",
        "-i", video_path,
        "-vf", f"select='not(mod(n\,{N}))'",
        "-vsync", "vfr",
        "-q:v", "2",
        output_pattern
    ]

    subprocess.run(cmd, capture_output=True, check=True)

    frames = sorted([
        os.path.join(output_dir, f)
        for f in os.listdir(output_dir)
        if f.endswith('.jpg')
    ])

    return frames

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

def transcribe_with_groq(audio_path: str, language: str = None) -> Dict:
    with open(audio_path, "rb") as audio_file:
        transcription = groq_client.audio.transcriptions.create(
            file=audio_file,
            model="whisper-large-v3-turbo",  # Fastest model
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
    Fast similarity search.
    """
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings.astype('float32'))
    
    # Save index to disk
    faiss.write_index(index, index_path)
    return index


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

# ===== Caption Generation (Optional - can be skipped for speed) =====

def generate_simple_captions(image_paths: List[str]) -> List[str]:
    """
    Generate simple captions based on frame numbers.
    For maximum speed, skip heavy captioning models.
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

    
        # Step 1: Extract keyframes using FFmpeg
        print("Extracting keyframes...")
        frame_paths = extract_keyframes_ffmpeg(video_path, frames_dir)
        self.frame_paths = frame_paths
        print(f"Extracted {len(frame_paths)} keyframes")

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

         # Step 6: Store frame metadata in ChromaDB
        print("Storing frame metadata...")
        frame_texts = [f"Frame {i+1} from video" for i in range(len(frame_paths))]
        frame_embeddings = generate_text_embeddings(frame_texts)
        frame_metadatas = [
            {
                "type": "frame",
                "video_id": video_id,
                "frame_path": frame_paths[i],
                "frame_index": i
            }
            for i in range(len(frame_paths))
        ]

        store_text_chromadb(
            texts=frame_texts,
            embeddings=frame_embeddings,
            metadatas=frame_metadatas,
            collection_name=f"frames_{video_id}"
        )



        print("Processing complete!")
        
        return {
            "status": "success",
            "video_id": video_id,
            "frames_extracted": len(frame_paths),
            "transcript_length": len(transcript_text),
            "segments_count": len(segments),
            "transcript": transcript_text,
            "faiss_index_path": faiss_index_path
        }
    

pipeline = VideoProcessingPipeline(
    storage_dir="mosaic/extracted_frames"
)

res = pipeline.process_video(
    video_path="mosaic/my_video.mp4.webm",
    video_id="video_001"
)

import pprint

pprint.pprint(res)