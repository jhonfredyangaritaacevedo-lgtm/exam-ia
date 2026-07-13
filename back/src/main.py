from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from core.config import settings
from core.database import engine, Base, check_database_connection
from routes.auth import router as auth_router
from routes.generate import router as generate_router
from routes.exams import router as exams_router
from routes.admin import router as admin_router
from models.user import User
from models.exam import Exam
from models.ebc_chunk import EbcChunk
from models.rag_document import RagDocument
from models.reindex_status import ReindexStatus
from models.password_reset import PasswordResetToken

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Check database connection
if not check_database_connection():
    logger.warning("⚠️  Database connection failed! The API will start but database operations will fail.")
    logger.warning("⚠️  Please check your DATABASE_URL configuration in .env file")
else:
    # Create database tables only if connection is successful
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created successfully")
    except Exception as e:
        logger.error(f"❌ Failed to create database tables: {e}")

# Create FastAPI app instance
app = FastAPI(
    title="ExamIA API",
    version="0.1.0",
    description="Sistema Inteligente de Generación de Exámenes con RAG Híbrido",
    debug=settings.DEBUG
)

# Configuración CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(generate_router)
app.include_router(exams_router)
app.include_router(admin_router)


@app.get("/")
def read_root():
    """Root endpoint"""
    return {
        "message": "Welcome to ExamIA API",
        "version": "0.1.0",
        "description": "Sistema Inteligente de Generación de Exámenes",
        "status": "running"
    }


@app.get("/health")
def health_check():
    """Health check endpoint with database status"""
    db_status = "connected" if check_database_connection() else "disconnected"
    overall_status = "healthy" if db_status == "connected" else "degraded"

    return {
        "status": overall_status,
        "service": "ExamIA API",
        "version": "0.1.0",
        "database": db_status
    }
