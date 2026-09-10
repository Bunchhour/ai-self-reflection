import logging
import asyncio
from typing import List

logger = logging.getLogger(__name__)

class EmbeddingService:
    _instance = None
    _model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EmbeddingService, cls).__new__(cls)
        return cls._instance

    def _get_model(self):
        if self._model is None:
            logger.info("Loading sentence-transformers model...")
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer("all-MiniLM-L6-v2")
            except Exception as e:
                logger.error(f"Failed to load embedding model: {e}")
                raise
        return self._model

    def _encode_sync(self, text: str) -> List[float]:
        """Synchronous encoding — called via asyncio.to_thread."""
        try:
            model = self._get_model()
            embedding = model.encode(text)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return []

    async def get_embedding_async(self, text: str) -> List[float]:
        """Non-blocking async wrapper that runs CPU-bound inference in a thread."""
        return await asyncio.to_thread(self._encode_sync, text)

    def get_embedding(self, text: str) -> List[float]:
        """Synchronous fallback for non-async contexts."""
        return self._encode_sync(text)

embedding_service = EmbeddingService()

def get_embedding(text: str) -> List[float]:
    return embedding_service.get_embedding(text)

async def get_embedding_async(text: str) -> List[float]:
    return await embedding_service.get_embedding_async(text)

