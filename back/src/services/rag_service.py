from sqlalchemy import text
from sqlalchemy.orm import Session
from .embedding_service import EmbeddingService
from models.ebc_chunk import EbcChunk
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class RagService:
    """Service to handle Retrieval Augmented Generation logic"""
    
    def __init__(self, db: Session):
        self.db = db
        self.embedding_service = EmbeddingService()

    def search_ebc(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for relevant EBC chunks based on semantic similarity
        
        Args:
            query: The search query (e.g., "Ciencias Naturales grado 10")
            limit: Number of results to return
            
        Returns:
            List of dictionaries with content and metadata
        """
        try:
            # 1. Generate embedding for the query
            query_embedding = self.embedding_service.get_embedding(query, task_type="RETRIEVAL_QUERY")
            
            # 2. Query pgvector using cosine distance (<=> operator)
            embedding_str = "[" + ",".join(map(str, query_embedding)) + "]"
            query_str = text("""
                SELECT id, area, grado, competencia, content,
                (embedding <=> CAST(:embedding AS vector)) as distance
                FROM ebc_chunks
                ORDER BY distance ASC
                LIMIT :limit
            """)

            results = self.db.execute(query_str, {
                "embedding": embedding_str,
                "limit": limit
            }).fetchall()
            
            # 3. Format results
            formatted_results = []
            for r in results:
                formatted_results.append({
                    "id": str(r.id),
                    "area": r.area,
                    "grado": r.grado,
                    "competencia": r.competencia,
                    "content": r.content,
                    "score": 1 - r.distance # Convert distance to similarity score
                })
                
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error during RAG search: {str(e)}")
            self.db.rollback()
            return []

    def build_rag_context(self, area: str, grado: str, topic: str) -> str:
        """
        Builds a comprehensive context string combining multiple EBC search results
        """
        search_query = f"Estándares básicos de competencias en {area} para grado {grado}. Tema: {topic}"
        relevant_chunks = self.search_ebc(search_query, limit=4)
        
        if not relevant_chunks:
            return ""
            
        context = "### LINEAMIENTOS OFICIALES DEL MEN (COLOMBIA):\n"
        for chunk in relevant_chunks:
            context += f"- [{chunk['area']} {chunk['grado']}]: {chunk['content']}\n\n"
            
        return context
