from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np
from PIL import Image

clip_model = SentenceTransformer('clip-ViT-B-32')


def generate_image_embeddings(image_paths: List[str]) -> np.ndarray:
    """
    Generate CLIP embeddings for images.
    Batch processing for speed.
    """
    images = [Image.open(img_path).convert('RGB') for img_path in image_paths]
    embeddings = clip_model.encode(images, batch_size=32, show_progress_bar=False)
    return embeddings

print(generate_image_embeddings(
    # list of image paths in extracted_frames dir dynamically
    ["mosaic/extracted_frames/frame_0001.jpg", "mosaic/extracted_frames/frame_0002.jpg"]
))
