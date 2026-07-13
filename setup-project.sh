#!/bin/bash

# Script de inicialización para personalizar el proyecto
# Uso: ./setup-project.sh

set -e

echo "🚀 MVP Base - Setup del Proyecto"
echo "=================================="
echo ""

# Obtener nombre del proyecto
read -p "📦 Nombre del proyecto (ej: mi-app): " PROJECT_NAME
if [ -z "$PROJECT_NAME" ]; then
    echo "❌ El nombre del proyecto es obligatorio"
    exit 1
fi

# Obtener descripción
read -p "📝 Descripción del proyecto: " DESCRIPTION

# Obtener información del autor
read -p "👤 Nombre del autor: " AUTHOR_NAME
read -p "📧 Email del autor: " AUTHOR_EMAIL

echo ""
echo "🔧 Configurando proyecto..."
echo ""

# 1. Actualizar pyproject.toml (Backend)
echo "📝 Actualizando backend/pyproject.toml..."
sed -i "s/name = \"mvp-base\"/name = \"$PROJECT_NAME\"/" back/pyproject.toml
sed -i "s/description = \"\"/description = \"$DESCRIPTION\"/" back/pyproject.toml

if [ ! -z "$AUTHOR_NAME" ]; then
    sed -i "s/name = \"Edinson Mendoza\"/name = \"$AUTHOR_NAME\"/" back/pyproject.toml
fi

if [ ! -z "$AUTHOR_EMAIL" ]; then
    sed -i "s/email = \"emmendoza2794@gmail.com\"/email = \"$AUTHOR_EMAIL\"/" back/pyproject.toml
fi

# 2. Actualizar package.json (Frontend)
echo "📝 Actualizando front/package.json..."
sed -i "s/\"name\": \"front\"/\"name\": \"$PROJECT_NAME-front\"/" front/package.json
sed -i "s/\"description\": \"\"/\"description\": \"$DESCRIPTION\"/" front/package.json

if [ ! -z "$AUTHOR_NAME" ]; then
    sed -i "s/\"author\": \"\"/\"author\": \"$AUTHOR_NAME\"/" front/package.json
fi

# 3. Actualizar template.yaml (AWS Lambda)
echo "📝 Actualizando back/template.yaml..."
sed -i "s/FunctionName: 'mvp-base-backend'/FunctionName: '$PROJECT_NAME-backend'/" back/template.yaml

# 4. Crear archivo .env de ejemplo para el backend
echo "📝 Creando back/.env.example..."
cat > back/.env.example << EOF
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/${PROJECT_NAME//-/_}

# Application Settings
DEBUG=True

# JWT Configuration
JWT_SECRET_KEY=change-this-secret-key-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=10080
EOF

# 5. Crear .env desde .env.example si no existe
if [ ! -f "back/.env" ]; then
    echo "📝 Creando back/.env..."
    cp back/.env.example back/.env
    echo "⚠️  Recuerda configurar las variables en back/.env"
fi

# 6. Actualizar README.md principal
echo "📝 Actualizando README.md..."
sed -i "s/# MVP Base/# $PROJECT_NAME/" README.md
if [ ! -z "$DESCRIPTION" ]; then
    sed -i "s/Full-stack boilerplate siguiendo principios de arquitectura limpia/$DESCRIPTION/" README.md
fi

if [ ! -z "$AUTHOR_NAME" ]; then
    sed -i "s/\*\*Edinson Mendoza\*\*/**$AUTHOR_NAME**/" README.md
fi

if [ ! -z "$AUTHOR_EMAIL" ]; then
    sed -i "s/emmendoza2794@gmail.com/$AUTHOR_EMAIL/" README.md
fi

# 7. Generar JWT Secret Key aleatorio
JWT_SECRET=$(openssl rand -hex 32 2>/dev/null || python3 -c "import secrets; print(secrets.token_hex(32))")
sed -i "s/JWT_SECRET_KEY=change-this-secret-key-in-production/JWT_SECRET_KEY=$JWT_SECRET/" back/.env

echo ""
echo "✅ ¡Proyecto configurado exitosamente!"
echo ""
echo "📋 Siguiente pasos:"
echo ""
echo "1. Backend:"
echo "   cd back"
echo "   pip install -r requirements.txt  # o poetry install"
echo "   # Configurar base de datos en .env"
echo "   uvicorn src.main:app --reload"
echo ""
echo "2. Frontend:"
echo "   cd front"
echo "   npm install"
echo "   npm run dev"
echo ""
echo "🔐 Se generó un JWT_SECRET_KEY aleatorio en back/.env"
echo "⚠️  Recuerda configurar DATABASE_URL en back/.env"
echo ""
echo "📚 Consulta README.md para más información"
echo ""
