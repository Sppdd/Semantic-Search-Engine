from typing import List, Optional
import numpy as np
import requests
from config import Config

class EmbeddingService:
    def __init__(self):
        self.api_url = "https://api-inference.huggingface.co/pipeline/feature-extraction/sentence-transformers/all-MiniLM-L6-v2"
        self.headers = {"Authorization": f"Bearer {Config.HF_API_TOKEN}"}

    def get_single_embedding(self, text: str) -> Optional[List[float]]:
        """Get embedding for a single piece of text."""
        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json={"inputs": text}
            )
            
            if response.status_code == 401:
                print(f"Authentication failed. Please check your Hugging Face API token.")
                print(f"Current token: {Config.HF_API_TOKEN[:10]}...")
                return None
                
            response.raise_for_status()
            embeddings = response.json()
            
            if isinstance(embeddings, list) and len(embeddings) > 0:
                return embeddings[0]
            return None
            
        except requests.exceptions.RequestException as e:
            print(f"Error getting embedding: {str(e)}")
            return None

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

    def get_embeddings(self, texts: List[str]) -> Optional[List[List[float]]]:
        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json={"inputs": texts}
            )
            response.raise_for_status()
            embeddings = response.json()
            return embeddings
        except Exception as e:
            print(f"Error getting embeddings: {e}")
            return None

    def get_single_embedding(self, text: str) -> Optional[List[float]]:
        embeddings = self.get_embeddings([text])
        return embeddings[0] if embeddings else None 