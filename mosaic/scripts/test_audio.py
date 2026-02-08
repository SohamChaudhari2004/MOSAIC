from groq import Groq
import os
import subprocess
from dotenv import load_dotenv
load_dotenv()
from typing import Dict
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def transcribe_with_groq(audio_path: str, language: str = "en") -> Dict:
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

print(transcribe_with_groq(
    "mosaic/Recording (2).m4a",
    language="en"
))