from google import genai
from google.genai import types
from core.config import settings
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)

class EmbeddingService:
    """Service to generate embeddings using Google's Gemini API"""
    
    def __init__(self):
        self.client = genai.Client(
            api_key=settings.GEMINI_API_KEY
        )
        self.model = settings.EMBEDDING_MODEL

    def get_embedding(self, text: str, task_type: str = "RETRIEVAL_DOCUMENT") -> List[float]:
        """
        Generate embedding for a single text string.
        
        Args:
            text: Text to embed
            task_type: Purpose of the embedding (RETRIEVAL_DOCUMENT or RETRIEVAL_QUERY)
            
        Returns:
            List of 768 floats
        """
        try:
            result = self.client.models.embed_content(
                model=self.model,
                contents=text,
                config=types.EmbedContentConfig(
                    task_type=task_type,
                    output_dimensionality=768
                )
            )
            return result.embeddings[0].values
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            raise

    def get_embeddings_batch(self, texts: List[str], task_type: str = "RETRIEVAL_DOCUMENT") -> List[List[float]]:
        """
        Generate embeddings for a batch of texts.
        
        Args:
            texts: List of strings
            task_type: Purpose of the embedding
            
        Returns:
            List of lists of 768 floats
        """
        try:
            result = self.client.models.embed_content(
                model=self.model,
                contents=texts,
                config=types.EmbedContentConfig(task_type=task_type)
            )
            return [e.values for e in result.embeddings]
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {str(e)}")
            raise
