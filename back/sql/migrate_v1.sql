-- 1. Crear ENUM user_role y migrar columna role en users
DO $$ BEGIN
    CREATE TYPE user_role AS ENUM ('teacher', 'admin');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

ALTER TABLE users 
    ALTER COLUMN role TYPE user_role USING role::user_role;

-- 2. Agregar columna updated_at a users
ALTER TABLE users 
    ADD COLUMN updated_at TIMESTAMP WITH TIME ZONE;

-- 3. Crear ENUM exam_status y migrar columna status en exams
DO $$ BEGIN
    CREATE TYPE exam_status AS ENUM ('pending', 'processing', 'successful', 'failed');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

ALTER TABLE exams 
    ALTER COLUMN status TYPE exam_status USING status::exam_status;

-- 4. Hacer prompt NOT NULL en exams
UPDATE exams SET prompt = '' WHERE prompt IS NULL;
ALTER TABLE exams 
    ALTER COLUMN prompt SET NOT NULL;
