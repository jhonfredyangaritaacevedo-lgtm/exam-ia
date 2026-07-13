-- Initial database setup script for ExamIA
-- This script creates the database schema with pgvector support

-- Enable the vector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'teacher',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE
);

-- Create exams table
CREATE TABLE IF NOT EXISTS exams (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id),
    title VARCHAR(255) NOT NULL,
    area VARCHAR(255) NOT NULL,
    grado VARCHAR(50) NOT NULL,
    prompt TEXT,
    num_questions INTEGER NOT NULL,
    question_types JSONB NOT NULL,
    files_uuid VARCHAR(255),
    result JSONB,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    tokens_in INTEGER,
    tokens_out INTEGER,
    duration_seconds INTEGER,
    model_used VARCHAR(255),
    deleted BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create rag_documents table (uploaded teacher documents metadata)
CREATE TABLE IF NOT EXISTS rag_documents (
    id UUID PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    s3_key VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'processed',
    uploaded_by UUID NOT NULL REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create ebc_chunks table (RAG - Static MEN Standards)
CREATE TABLE IF NOT EXISTS ebc_chunks (
    id UUID PRIMARY KEY,
    area VARCHAR(255) NOT NULL,
    grado VARCHAR(50) NOT NULL,
    competencia TEXT NOT NULL,
    content TEXT NOT NULL,
    embedding vector(768)
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_exams_user_id ON exams(user_id);
CREATE INDEX IF NOT EXISTS idx_ebc_chunks_area_grado ON ebc_chunks(area, grado);

-- Vector similarity indexes (HNSW)
CREATE INDEX ON ebc_chunks USING hnsw (embedding vector_cosine_ops);
