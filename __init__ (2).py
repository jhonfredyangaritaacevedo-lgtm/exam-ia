-- script para limpiar la base de datos y empezar de cero con el nuevo esquema de UUIDs
DROP TABLE IF EXISTS rag_documents CASCADE;
DROP TABLE IF EXISTS ebc_chunks CASCADE;
DROP TABLE IF EXISTS exams CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TYPE IF EXISTS user_role CASCADE;
DROP TYPE IF EXISTS exam_status CASCADE;

CREATE EXTENSION IF NOT EXISTS vector;
