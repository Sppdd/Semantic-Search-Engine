from typing import List, Optional
import numpy as np
import requests
from config import Config
from sentence_transformers import SentenceTransformer
import os
import time

class EmbeddingService:
    def __init__(self):
        # Initialize the local model as a fallback
        self.local_model = None
        self.api_url = "https://api-inference.huggingface.co/pipeline/feature-extraction/sentence-transformers/all-MiniLM-L6-v2"
        self.api_key = os.getenv("HUGGINGFACE_API_KEY")
        self.headers = {"Authorization": f"Bearer {self.api_key}"}

    def _ensure_local_model(self):
        """Ensure local model is loaded"""
        if self.local_model is None:
            self.local_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

    def get_single_embedding(self, text: str):
        """Get embedding for a single text using API first, falling back to local model"""
        try:
            # Try API first
            response = requests.post(self.api_url, headers=self.headers, json={"inputs": text})
            
            if response.status_code == 200:
                return response.json()
                
            # If API fails, use local model
            self._ensure_local_model()
            embedding = self.local_model.encode([text])[0]
            return embedding.tolist()
            
        except Exception as e:
            # If any error occurs, use local model
            self._ensure_local_model()
            embedding = self.local_model.encode([text])[0]
            return embedding.tolist()

    def get_embeddings(self, texts: list):
        """Get embeddings for multiple texts"""
        try:
            # Try API first
            response = requests.post(self.api_url, headers=self.headers, json={"inputs": texts})
            
            if response.status_code == 200:
                return response.json()
                
            # If API fails, use local model
            self._ensure_local_model()
            embeddings = self.local_model.encode(texts)
            return embeddings.tolist()
            
        except Exception as e:
            # If any error occurs, use local model
            self._ensure_local_model()
            embeddings = self.local_model.encode(texts)
            return embeddings.tolist()

    def get_batch_embeddings(self, texts: List[str]) -> List[Optional[List[float]]]:
        """Get embeddings for multiple texts."""
        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json={"inputs": texts, "options": {"wait_for_model": True}}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error getting batch embeddings: {e}")
            return [None] * len(texts)

    def get_single_embedding(self, text: str) -> Optional[List[float]]:
        embeddings = self.get_embeddings([text])
        return embeddings[0] if embeddings else None 