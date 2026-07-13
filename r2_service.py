import time
import sys
import os
import requests
import uuid
import logging
from sqlalchemy.orm import Session

# Add src/ to path so absolute imports (core, models, services) work
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from core.database import SessionLocal, Base, engine
from models.ebc_chunk import EbcChunk
from services.document_extractor import DocumentExtractorService
from services.embedding_service import EmbeddingService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Official MEN EBC PDF URL (Wayback Machine)
EBC_PDF_URL = "https://web.archive.org/web/20220619192236if_/https://www.mineducacion.gov.co/1621/articles-340021_recurso_1.pdf"

def download_pdf(url: str, output_path: str):
    logger.info(f"Downloading EBC PDF from {url}...")
    response = requests.get(url)
    response.raise_for_status()
    with open(output_path, "wb") as f:
        f.write(response.content)
    logger.info(f"PDF saved to {output_path}")

def chunk_markdown(md_text: str, chunk_size: int = 1500) -> list:
    """Simple chunking by character count, trying to respect paragraphs"""
    chunks = []
    paragraphs = md_text.split("\n\n")
    current_chunk = ""
    
    for p in paragraphs:
        if len(current_chunk) + len(p) < chunk_size:
            current_chunk += p + "\n\n"
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = p + "\n\n"
            
    if current_chunk:
        chunks.append(current_chunk.strip())
        
    return chunks

def index_ebc():
    db = SessionLocal()
    extractor = DocumentExtractorService()
    embedding_service = EmbeddingService()
    
    local_pdf = "ebc_lineamientos.pdf"
    
    try:
        # 1. Download
        if not os.path.exists(local_pdf):
            download_pdf(EBC_PDF_URL, local_pdf)
        
        # 2. Extract to Markdown
        logger.info("Extracting text to Markdown using MarkItDown...")
        md_content = extractor.extract_to_markdown(local_pdf)
        if not md_content:
            logger.error("Failed to extract content from PDF")
            return

        # 3. Chunking
        logger.info("Chunking content...")
        chunks = chunk_markdown(md_content)
        logger.info(f"Created {len(chunks)} chunks")

        # 4. Embed and Save
        logger.info("Generating embeddings and saving to database...")
        for i, chunk_text in enumerate(chunks):
            try:
                # Check if chunk already exists to allow resuming
                existing = db.query(EbcChunk).filter(EbcChunk.content == chunk_text).first()
                if existing:
                    continue

                # Add a small delay to avoid 429 Rate Limit (Free Tier: 15 RPM)
                # We sleep 5s every chunk to be extremely safe
                time.sleep(5)

                embedding = embedding_service.get_embedding(chunk_text)
                
                ebc_chunk = EbcChunk(
                    id=uuid.uuid4(),
                    area="General", # Initial classification
                    grado="9-11",
                    competencia="Lineamiento General",
                    content=chunk_text,
                    embedding=embedding
                )
                db.add(ebc_chunk)
                
                if i % 10 == 0:
                    db.commit()
                    logger.info(f"Processed {i}/{len(chunks)} chunks...")
            except Exception as e:
                logger.error(f"Error processing chunk {i}: {str(e)}")
                db.rollback()

        db.commit()
        logger.info("Indexation completed successfully!")

    except Exception as e:
        logger.error(f"Fatal error during indexation: {str(e)}")
    finally:
        db.close()
        if os.path.exists(local_pdf):
            os.remove(local_pdf)

if __name__ == "__main__":
    index_ebc()
