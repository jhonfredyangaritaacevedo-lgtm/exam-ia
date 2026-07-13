import uuid
import os
import json
import tempfile
import threading
import logging
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session

from core.database import get_db, SessionLocal
from core.auth import require_admin
from models.rag_document import RagDocument
from models.ebc_chunk import EbcChunk
from models.reindex_status import ReindexStatus
from repositories.rag_document_repository import RagDocumentRepository
from services.r2_service import r2_service
from services.document_extractor import DocumentExtractorService
from services.embedding_service import EmbeddingService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["Admin"])


def _get_status_row(db: Session) -> ReindexStatus:
    """Obtiene (o crea) la fila singleton de estado de re-indexación."""
    row = db.query(ReindexStatus).filter(ReindexStatus.id == 1).first()
    if not row:
        row = ReindexStatus(id=1, running=False, progress="Sin ejecutar", error=None)
        db.add(row)
        db.commit()
    return row


def _set_status(db: Session, *, running: bool, progress: str, error=None):
    row = _get_status_row(db)
    row.running = running
    row.progress = progress
    row.error = error
    db.commit()


@router.get("/rag/stats")
def get_rag_stats(db: Session = Depends(get_db), _=Depends(require_admin)):
    return {
        "documents": db.query(RagDocument).count(),
        "chunks": db.query(EbcChunk).count(),
    }


@router.get("/rag/documents")
def list_rag_documents(db: Session = Depends(get_db), _=Depends(require_admin)):
    docs = db.query(RagDocument).order_by(RagDocument.created_at.desc()).all()
    return [
        {
            "id": str(d.id),
            "filename": d.filename,
            "s3_key": d.s3_key,
            "status": d.status,
            "created_at": d.created_at.isoformat() if d.created_at else None,
        }
        for d in docs
    ]


@router.post("/rag/upload", status_code=status.HTTP_201_CREATED)
async def upload_rag_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin),
):
    allowed = {".pdf", ".docx", ".pptx", ".xlsx"}
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in allowed:
        raise HTTPException(status_code=400, detail=f"Tipo de archivo no permitido: {ext}")

    content = await file.read()
    s3_key = r2_service.upload_file(content, file.filename)

    repo = RagDocumentRepository(db)
    doc = repo.add_document(
        user_id=uuid.UUID(current_user["user_id"]),
        filename=file.filename,
        s3_key=s3_key,
    )
    return {"id": str(doc.id), "filename": doc.filename, "status": doc.status}


@router.get("/rag/documents/{doc_id}/download")
def download_rag_document(
    doc_id: uuid.UUID,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    from fastapi.responses import StreamingResponse
    import io

    doc = db.query(RagDocument).filter(RagDocument.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Documento no encontrado")

    file_bytes = r2_service.download_file(doc.s3_key)
    return StreamingResponse(
        io.BytesIO(file_bytes),
        media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{doc.filename}"'},
    )


@router.delete("/rag/documents/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rag_document(
    doc_id: uuid.UUID,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    doc = db.query(RagDocument).filter(RagDocument.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    try:
        r2_service.delete_file(doc.s3_key)
    except Exception as e:
        logger.warning(f"No se pudo eliminar de R2: {e}")
    db.delete(doc)
    db.commit()


@router.post("/rag/reindex")
def trigger_reindex(
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    row = _get_status_row(db)
    if row.running:
        raise HTTPException(status_code=400, detail="Re-indexación ya en progreso")

    _set_status(db, running=True, progress="Iniciando...", error=None)

    if os.getenv("AWS_LAMBDA_FUNCTION_NAME"):
        import boto3
        client = boto3.client("lambda")
        client.invoke(
            FunctionName=os.environ["AWS_LAMBDA_FUNCTION_NAME"],
            InvocationType="Event",
            Payload=json.dumps({"task": "reindex"}),
        )
    else:
        threading.Thread(target=run_reindex, daemon=True).start()

    return {"message": "Re-indexación iniciada"}


@router.post("/rag/documents/{doc_id}/reindex")
def trigger_reindex_single(
    doc_id: uuid.UUID,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    row = _get_status_row(db)
    if row.running:
        raise HTTPException(status_code=400, detail="Re-indexación ya en progreso")

    doc = db.query(RagDocument).filter(RagDocument.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Documento no encontrado")

    _set_status(db, running=True, progress="Iniciando...", error=None)

    if os.getenv("AWS_LAMBDA_FUNCTION_NAME"):
        import boto3
        client = boto3.client("lambda")
        client.invoke(
            FunctionName=os.environ["AWS_LAMBDA_FUNCTION_NAME"],
            InvocationType="Event",
            Payload=json.dumps({"task": "reindex_single", "doc_id": str(doc_id)}),
        )
    else:
        threading.Thread(target=run_reindex_single, args=(doc_id,), daemon=True).start()

    return {"message": "Re-indexación iniciada"}


@router.get("/rag/reindex/status")
def get_reindex_status(db: Session = Depends(get_db), _=Depends(require_admin)):
    row = _get_status_row(db)
    return {"running": row.running, "progress": row.progress, "error": row.error}


def _chunk_text(text: str, chunk_size: int = 1500) -> list[str]:
    chunks = []
    current = ""
    for paragraph in text.split("\n\n"):
        if len(current) + len(paragraph) < chunk_size:
            current += paragraph + "\n\n"
        else:
            if current:
                chunks.append(current.strip())
            current = paragraph + "\n\n"
    if current:
        chunks.append(current.strip())
    return chunks


def run_reindex_single(doc_id: uuid.UUID):
    """Re-indexa un único documento. Entrypoint para la auto-invocación de Lambda."""
    db = SessionLocal()
    extractor = DocumentExtractorService()
    embedding_service = EmbeddingService()

    try:
        doc = db.query(RagDocument).filter(RagDocument.id == doc_id).first()
        if not doc:
            _set_status(db, running=False, progress="Error", error="Documento no encontrado")
            return

        _set_status(db, running=True, progress=f"Eliminando chunks anteriores de {doc.filename}...", error=None)
        db.query(EbcChunk).filter(EbcChunk.competencia == doc.filename).delete()
        db.commit()

        _set_status(db, running=True, progress=f"Extrayendo contenido de {doc.filename}...", error=None)
        file_bytes = r2_service.download_file(doc.s3_key)
        ext = os.path.splitext(doc.filename)[1]
        with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
            tmp.write(file_bytes)
            tmp_path = tmp.name

        try:
            md_content = extractor.extract_to_markdown(tmp_path)
        finally:
            os.unlink(tmp_path)

        if not md_content:
            _set_status(db, running=False, progress="Error", error=f"No se pudo extraer contenido de {doc.filename}")
            return

        chunks = _chunk_text(md_content)
        total_chunks = 0
        for i, chunk_text in enumerate(chunks):
            try:
                embedding = embedding_service.get_embedding(chunk_text)
                db.add(EbcChunk(
                    id=uuid.uuid4(),
                    area="General",
                    grado="9-11",
                    competencia=doc.filename,
                    content=chunk_text,
                    embedding=embedding,
                ))
                total_chunks += 1
                if total_chunks % 10 == 0:
                    db.commit()
                    _set_status(db, running=True, progress=f"Procesando {doc.filename} — {i+1}/{len(chunks)} chunks...", error=None)
            except Exception as e:
                logger.error(f"Error en chunk {i} de {doc.filename}: {e}")

        db.commit()
        _set_status(db, running=False, progress=f"Completado: {total_chunks} chunks de {doc.filename}", error=None)
        logger.info(f"Re-indexación de {doc.filename} completada: {total_chunks} chunks")

    except Exception as e:
        logger.error(f"Error en re-indexación de {doc_id}: {e}")
        db.rollback()
        _set_status(db, running=False, progress="Error", error=str(e))
    finally:
        db.close()


def run_reindex():
    """Ejecuta la re-indexación completa. Entrypoint para la auto-invocación de Lambda."""
    db = SessionLocal()
    extractor = DocumentExtractorService()
    embedding_service = EmbeddingService()

    try:
        docs = db.query(RagDocument).all()
        if not docs:
            _set_status(db, running=False, progress="Sin documentos para indexar", error=None)
            return

        _set_status(db, running=True, progress="Limpiando índice anterior...", error=None)
        db.query(EbcChunk).delete()
        db.commit()

        total_chunks = 0
        for doc_idx, doc in enumerate(docs, 1):
            _set_status(db, running=True, progress=f"Procesando {doc.filename} ({doc_idx}/{len(docs)})...", error=None)
            logger.info(f"Indexando: {doc.filename}")

            file_bytes = r2_service.download_file(doc.s3_key)

            ext = os.path.splitext(doc.filename)[1]
            with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
                tmp.write(file_bytes)
                tmp_path = tmp.name

            try:
                md_content = extractor.extract_to_markdown(tmp_path)
            finally:
                os.unlink(tmp_path)

            if not md_content:
                logger.warning(f"No se extrajo contenido de {doc.filename}")
                continue

            chunks = _chunk_text(md_content)
            for i, chunk_text in enumerate(chunks):
                try:
                    embedding = embedding_service.get_embedding(chunk_text)
                    db.add(EbcChunk(
                        id=uuid.uuid4(),
                        area="General",
                        grado="9-11",
                        competencia=doc.filename,
                        content=chunk_text,
                        embedding=embedding,
                    ))
                    total_chunks += 1
                    if total_chunks % 10 == 0:
                        db.commit()
                        _set_status(db, running=True, progress=f"Procesando {doc.filename} — {i+1}/{len(chunks)} chunks...", error=None)
                except Exception as e:
                    logger.error(f"Error en chunk {i} de {doc.filename}: {e}")

        db.commit()
        _set_status(db, running=False, progress=f"Completado: {total_chunks} chunks de {len(docs)} documentos", error=None)
        logger.info(f"Re-indexación completada: {total_chunks} chunks")

    except Exception as e:
        logger.error(f"Error fatal en re-indexación: {e}")
        db.rollback()
        _set_status(db, running=False, progress="Error", error=str(e))
    finally:
        db.close()
