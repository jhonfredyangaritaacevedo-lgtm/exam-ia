#!/bin/bash

# Script para desplegar ExamIA Backend a AWS Lambda

echo "🚀 Desplegando ExamIA Backend a AWS Lambda..."

# Verificar que Poetry esté instalado
if ! command -v poetry &> /dev/null; then
    echo "❌ Poetry no está instalado. Por favor instálalo primero:"
    echo "   curl -sSL https://install.python-poetry.org | python3 -"
    exit 1
fi

# Verificar que SAM CLI esté instalado
if ! command -v sam &> /dev/null; then
    echo "❌ SAM CLI no está instalado. Por favor instálalo primero:"
    echo "   pip install aws-sam-cli"
    exit 1
fi

# Verificar que AWS CLI esté configurado
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS CLI no está configurado. Por favor configúralo primero:"
    echo "   aws configure"
    exit 1
fi

# Generar requirements.txt desde el virtualenv de Poetry
echo "📋 Generando requirements.txt..."
poetry run pip freeze > requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Error generando requirements.txt"
    exit 1
fi

echo "✅ requirements.txt generado exitosamente"

# Build del proyecto
echo "📦 Construyendo el proyecto..."
sam build

if [ $? -ne 0 ]; then
    echo "❌ Error en el build"
    exit 1
fi

# Cargar variables de entorno para los parámetros del template (no se commitean)
if [ -f .env ]; then
    set -a
    source .env
    set +a
fi

for var in DATABASE_URL JWT_SECRET_KEY JWT_REFRESH_SECRET_KEY GEMINI_API_KEY \
           CLOUDFLARE_R2_ACCOUNT_ID CLOUDFLARE_R2_ACCESS_KEY_ID CLOUDFLARE_R2_SECRET_ACCESS_KEY \
           CLOUDFLARE_R2_BUCKET_NAME CLOUDFLARE_R2_PUBLIC_URL RESEND_API_KEY EMAIL_FROM FRONTEND_URL; do
    if [ -z "${!var}" ]; then
        echo "❌ Falta la variable de entorno $var (defínela en back/.env)"
        exit 1
    fi
done

# Deploy del proyecto
echo "🚀 Desplegando a AWS..."
sam deploy --parameter-overrides \
    DatabaseUrl="$DATABASE_URL" \
    JwtSecretKey="$JWT_SECRET_KEY" \
    JwtRefreshSecretKey="$JWT_REFRESH_SECRET_KEY" \
    GeminiApiKey="$GEMINI_API_KEY" \
    CloudflareR2AccountId="$CLOUDFLARE_R2_ACCOUNT_ID" \
    CloudflareR2AccessKeyId="$CLOUDFLARE_R2_ACCESS_KEY_ID" \
    CloudflareR2SecretAccessKey="$CLOUDFLARE_R2_SECRET_ACCESS_KEY" \
    CloudflareR2BucketName="$CLOUDFLARE_R2_BUCKET_NAME" \
    CloudflareR2PublicUrl="$CLOUDFLARE_R2_PUBLIC_URL" \
    ResendApiKey="$RESEND_API_KEY" \
    EmailFrom="$EMAIL_FROM" \
    FrontendUrl="$FRONTEND_URL"

if [ $? -eq 0 ]; then
    echo "✅ Deployment exitoso!"
    echo "🌐 Tu API está disponible en la URL mostrada arriba"
else
    echo "❌ Error en el deployment"
    exit 1
fi
