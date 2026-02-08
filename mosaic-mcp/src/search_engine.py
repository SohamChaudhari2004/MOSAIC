import os
from PIL import Image
import numpy as np
from sentence_transformers import SentenceTransformer
import chromadb
import faiss
import subprocess
import tempfile
from typing import List, Dict
import json
import pprint


class MultimodalSearchEngine:
    def __init__(self, storage_dir: str = "./storage"):
        self.storage_dir = storage_dir
        self.clip_model = SentenceTransformer('clip-ViT-B-32')
        self.text_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.chroma_client = chromadb.PersistentClient(path="./chroma_db")
        self.faiss_index = None
        self.frame_paths = []
        self.frame_timestamps = []

    def load_faiss_index(self, video_id: str):
        """
        Load FAISS index, frame paths, and timestamps for given video_id.
        """
        video_dir = os.path.join(self.storage_dir, video_id)
        faiss_index_path = os.path.join(video_dir, "faiss_index.bin")

        if not os.path.exists(faiss_index_path):
            raise FileNotFoundError(f"FAISS index not found for {video_id}")

        self.faiss_index = faiss.read_index(faiss_index_path)

        # Load frame paths from frames directory
        frames_dir = os.path.join(video_dir, "frames")
        self.frame_paths = sorted([
            os.path.join(frames_dir, f) for f in os.listdir(frames_dir) if f.endswith(".jpg")
        ])

        # Load frame timestamps if available
        self.load_frame_timestamps(video_dir)

    def load_frame_timestamps(self, video_dir: str):
        """
        Loads frame timestamps from a JSON file or similar associated with video frames.
        Assumes file 'frame_timestamps.json' in video directory with list of floats.
        """
        timestamps_path = os.path.join(video_dir, "frame_timestamps.json")
        if os.path.exists(timestamps_path):
            with open(timestamps_path, "r") as f:
                self.frame_timestamps = json.load(f)
            print(f"Loaded {len(self.frame_timestamps)} frame timestamps.")
        else:
            # If no timestamps file, clear or set empty - fallback to FPS-based timestamps later
            self.frame_timestamps = []
            print(f"Warning: frame_timestamps.json not found in {video_dir}. Timestamps fallback will be used.")

    def search_text(self, query: str, video_id: str, k: int = 5):
        """
        Search for text in the video transcript.
        """
        collection_name = f"video_{video_id}"
        try:
            collection = self.chroma_client.get_collection(name=collection_name)
        except:
            raise ValueError(f"Transcript collection not found for video '{video_id}'")

        results = collection.query(
            query_texts=[query],
            n_results=k,
            where={"type": "transcript_segment"}
        )
        
        hits = []
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0]
        ):
            hits.append({
                "text": doc,
                "start": meta.get("start"),
                "end": meta.get("end"),
                "distance": dist
            })
        return hits
    


    def search_image(self, query_image_path: str, video_id: str, k: int = 5, fps: float = 30.0):
        """Search frames using image similarity (CLIP embeddings)."""
        if self.faiss_index is None or not self.frame_paths:
            self.load_faiss_index(video_id)

        image = Image.open(query_image_path).convert('RGB')
        query_embedding = self.clip_model.encode([image])

        distances, indices = self.faiss_index.search(query_embedding.astype('float32'), k)

        results = []
        for idx, dist in zip(indices[0], distances[0]):
            if idx < len(self.frame_paths):
                timestamp = None
                if hasattr(self, 'frame_timestamps') and len(self.frame_timestamps) > idx:
                    timestamp = self.frame_timestamps[idx]

                # Fallback to fps if no timestamp found
                if timestamp is None:
                    timestamp = idx / fps

                clip_start, clip_duration = get_clip_params(timestamp)
                results.append({
                    "frame_path": self.frame_paths[idx],
                    "distance": float(dist),
                    "frame_index": int(idx),
                    "timestamp": timestamp,
                    "clip_start": clip_start,
                    "clip_duration": clip_duration
                })
        return results
    
    def search_visual(self, query_text: str, video_id: str, k: int = 5, fps: float = 30.0):
        """
        Search frames using text query with CLIP embeddings.
        This performs visual-semantic search - find frames that visually match the text description.
        More powerful than caption-based search as it uses CLIP's visual understanding.
        
        Args:
            query_text: Text description of what to find (e.g., "a person waving")
            video_id: ID of the video to search
            k: Number of results to return
            fps: Frames per second for timestamp calculation
            
        Returns:
            List of matching frames with paths, distances, timestamps, and clip parameters
        """
        if self.faiss_index is None or not self.frame_paths:
            self.load_faiss_index(video_id)

        # Encode text query using CLIP (same model used for image embeddings)
        query_embedding = self.clip_model.encode([query_text])

        distances, indices = self.faiss_index.search(query_embedding.astype('float32'), k)

        results = []
        for idx, dist in zip(indices[0], distances[0]):
            if idx < len(self.frame_paths):
                timestamp = None
                if hasattr(self, 'frame_timestamps') and len(self.frame_timestamps) > idx:
                    timestamp = self.frame_timestamps[idx]

                # Fallback to fps if no timestamp found
                if timestamp is None:
                    timestamp = idx / fps

                clip_start, clip_duration = get_clip_params(timestamp)
                results.append({
                    "frame_path": self.frame_paths[idx],
                    "distance": float(dist),
                    "frame_index": int(idx),
                    "timestamp": timestamp,
                    "clip_start": clip_start,
                    "clip_duration": clip_duration,
                    "search_type": "visual_clip"
                })
        return results
    
    def summarize_video(self, video_id: str, max_length: int = 100):
        collection_name = f"video_{video_id}"
        try:
            collection = self.chroma_client.get_collection(name=collection_name)
        except Exception as e:
            raise ValueError(f"Transcript collection not found for video '{video_id}': {e}")

        # Retrieve all transcript segments
        results = collection.query(
            n_results=1000,  # Arbitrary large number to get all segments
            where={"type": "transcript_segment"}
        )

        full_transcript = " ".join(results["documents"][0])
        
        # Simple summarization by truncation (replace with actual summarization model if needed)
        summary = " ".join(full_transcript.split()[:max_length])
        return {
            "status": "success",
            "video_id": video_id,
            "summary": summary
        }

    def search_caption(self, query: str, video_id: str, k: int = 5, fps: float = 30.0):
        collection_name = f"frames_{video_id}"
        try:
            collection = self.chroma_client.get_collection(name=collection_name)
        except Exception as e:
            raise ValueError(f"Frame captions collection not found for video '{video_id}': {e}")

        results = collection.query(
            query_texts=[query],
            n_results=k,
            where={"type": "frame"}
        )

        hits = []
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0]
        ):
            timestamp = meta.get("timestamp") or meta.get("start")

            # Fallback to frame index if no timestamp
            if (timestamp is None) and (meta.get("frame_index") is not None):
                timestamp = meta.get("frame_index") / fps

            if timestamp is not None:
                clip_start, clip_duration = get_clip_params(timestamp)
            else:
                clip_start, clip_duration = None, None

            hits.append({
                "caption": doc,
                "frame_path": meta.get("frame_path"),
                "frame_index": meta.get("frame_index"),
                "distance": dist,
                "timestamp": timestamp,
                "clip_start": clip_start,
                "clip_duration": clip_duration
            })
        return hits

    def search_audio(self, audio_path: str, video_id: str, k: int = 5):
        """
        Search video by audio similarity: transcribe the query audio clip,
        then search the transcript for matching text.
        
        Args:
            audio_path: Path to query audio file (wav, mp3, etc.)
            video_id: ID of the video to search
            k: Number of results to return
            
        Returns:
            List of matching transcript segments with timestamps
        """
        from video_processor import groq_client
        
        try:
            # Transcribe the uploaded audio clip
            with open(audio_path, "rb") as audio_file:
                transcription = groq_client.audio.transcriptions.create(
                    file=audio_file,
                    model="whisper-large-v3-turbo",
                    response_format="verbose_json",
                    timestamp_granularities=["segment"],
                    temperature=0.0
                )
            
            query_text = transcription.text.strip()
            
            if not query_text:
                return [{
                    "error": "Could not transcribe the audio clip. No speech detected.",
                    "query_text": "",
                    "search_type": "audio"
                }]
            
            # Search the transcript using the transcribed text
            results = self.search_text(query=query_text, video_id=video_id, k=k)
            
            # Add metadata about the audio search
            for hit in results:
                hit["search_type"] = "audio"
                hit["query_transcription"] = query_text
            
            return results
            
        except Exception as e:
            return [{
                "error": f"Audio search failed: {str(e)}",
                "search_type": "audio"
            }]


def get_clip_params(timestamp, pre_sec=1.0, clip_sec=5.0):
    """
    Calculate clip start time and duration for given center timestamp.
    Ensures start time is not negative.
    """
    start = max(timestamp - pre_sec, 0)
    duration = clip_sec
    return start, duration


def get_video_clips_from_hits(
    video_path: str,
    hits: List[Dict],
    output_dir: str,
    prefix: str = "clip"
) -> List[str]:
    """
    Extract video clips from original video corresponding to search hits.

    Args:
        video_path: Path to the original video file.
        hits: List of hits with 'start'/'end' keys (transcript) or 'timestamp' key (frames/captions).
        output_dir: Directory to save the clipped video files.
        prefix: Prefix for clip filenames.

    Returns:
        List of file paths to the extracted clips.
    """
    os.makedirs(output_dir, exist_ok=True)
    clip_paths = []

    for i, hit in enumerate(hits):
        if 'start' in hit and 'end' in hit:  # Transcript hits
            start_time = hit['start']
            end_time = hit['end']
            duration = end_time - start_time
        elif 'clip_start' in hit and 'clip_duration' in hit and hit['clip_start'] is not None:
            start_time = hit['clip_start']
            duration = hit['clip_duration']
        elif 'timestamp' in hit and hit['timestamp'] is not None:
            start_time, duration = get_clip_params(hit['timestamp'])
        else:
            print(f"Hit #{i+1} missing timing info, skipping clip creation.")
            continue

        output_path = os.path.join(output_dir, f"{prefix}_{i+1}.mp4")

        # Run FFmpeg clip command here (using re-encoding for compatibility)
        cmd = [
            "ffmpeg",
            "-i", video_path,
            "-ss", str(start_time),
            "-t", str(duration),
            "-c:v", "libx264",
            "-c:a", "aac",
            "-y",
            output_path
        ]
        
        print(f"Generating clip {i+1}: {start_time:.2f}s to {start_time + duration:.2f}s -> {output_path}")
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            if os.path.exists(output_path):
                clip_paths.append(output_path)
                print(f"  ✓ Clip generated: {output_path}")
            else:
                print(f"  ✗ Clip file not created: {output_path}")
        except subprocess.CalledProcessError as e:
            print(f"  ✗ FFmpeg error for clip {i+1}: {e.stderr}")
            continue

    return clip_paths


# Example usage

# if __name__ == "__main__":
#     search_engine = MultimodalSearchEngine(storage_dir="mosaic/extracted_frames")
#     # Replace these with your actual values
#     query_image = "mosaic/image.png"
#     video_id = "video_001"
#     fps = 30.0
#     video_file = "mosaic/my_video.mp4.webm"
#     output_clips_dir = "clips_output"

#     image_results = search_engine.search_image(query_image_path=query_image, video_id=video_id, k=3, fps=fps)
#     pprint.pprint(image_results)

#     # Generate clips for hits
#     clips = get_video_clips_from_hits(
#         video_path=video_file,
#         hits=image_results,
#         output_dir=output_clips_dir,
#         prefix="image_clip"
#     )
#     print(f"Extracted {len(clips)} clips to '{output_clips_dir}'")
