from typing import List, Dict, Any
from pinecone import Pinecone, ServerlessSpec
from config import Config

class VectorStore:
    def __init__(self):
        self.pc = Pinecone(api_key=Config.PINECONE_API_KEY)
        self.index_name = Config.PINECONE_INDEX_NAME
        self._ensure_index_exists()
        self.index = self.pc.Index(self.index_name)

    def _ensure_index_exists(self):
        """Ensure the Pinecone index exists, create if it doesn't."""
        if self.index_name not in self.pc.list_indexes().names():
            self.pc.create_index(
                name=self.index_name,
                dimension=384,  # Dimension for all-MiniLM-L6-v2 model
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="gcp",
                    region=Config.PINECONE_ENVIRONMENT
                )
            )

    def upsert(self, vectors: List[tuple[str, List[float], Dict[str, Any]]]):
        """
        Upsert vectors to the index.
        vectors: List of tuples (id, embedding, metadata)
        """
        batch_size = Config.BATCH_SIZE
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i + batch_size]
            self.index.upsert(vectors=batch)

    def search(self, query_vector: List[float], top_k: int = 5):
        """Search for similar vectors."""
        return self.index.query(
            vector=query_vector,
            top_k=top_k,
            include_metadata=True
        ) 