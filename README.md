# ExamIA

**ExamIA** es un sistema web basado en Inteligencia Artificial para la generación automática de exámenes, orientado a la educación media en Colombia (grados 9.º, 10.º y 11.º). Permite a los docentes crear evaluaciones de calidad a partir de sus propios materiales de clase (PDF, Word, PowerPoint, Excel) o mediante instrucciones en lenguaje natural, sin necesitar conocimientos técnicos en IA.

El sistema integra un pipeline de **RAG Híbrido** (Retrieval-Augmented Generation) que combina el material aportado por el docente con los Estándares Básicos de Competencias del Ministerio de Educación Nacional (MEN) de Colombia, garantizando exámenes alineados con el currículo oficial. Soporta preguntas de opción múltiple, verdadero/falso, respuesta corta y ensayo, todas editables antes de exportarse en Word o PDF.

Construido con arquitectura en capas (FastAPI + PostgreSQL en el backend, Nuxt 4 + PrimeVue en el frontend) y pensado para despliegue serverless en AWS Lambda y Cloudflare Workers.

## 📋 Tabla de Contenidos

- [Descripción](#-descripción)
- [Arquitectura](#-arquitectura)
- [Stack Tecnológico](#-stack-tecnológico)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Requisitos](#-requisitos)
- [Instalación](#-instalación)
- [Desarrollo](#-desarrollo)
- [Despliegue](#-despliegue)
- [Configuración](#-configuración)

## 🎯 Descripción

**ExamIA** está construido siguiendo mejores prácticas de desarrollo. Incluye:

- ✅ Backend con arquitectura en capas (Layered Architecture)
- ✅ Frontend moderno con Nuxt 4
- ✅ Sistema de autenticación JWT con Form Data
- ✅ Base de datos PostgreSQL con SQLAlchemy
- ✅ Health check con verificación de BD
- ✅ UI components con PrimeVue y Tailwind CSS
- ✅ Listo para despliegue serverless
- ✅ TypeScript en frontend
- ✅ Gestión de estado con Pinia
- ✅ Soporte PWA
- ✅ Script de setup automático
- ✅ Navegación responsive: sidebar desktop + barra inferior mobile + drawer con overlay
- ✅ Header global con avatar de usuario y menú contextual
- ✅ Landing page y página de documentación incluidas

## 🏗️ Arquitectura

### Backend (Arquitectura en Capas)

```
Routes → Services → Repositories → Models
   ↓         ↓
Schemas   Core (Config, DB, Utils)
```

**Capas:**
- **Routes**: Manejo de requests/responses HTTP (Form Data)
- **Services**: Lógica de negocio
- **Repositories**: Acceso a datos y operaciones de BD
- **Models**: Definición de entidades (SQLAlchemy)
- **Schemas**: Validación y serialización (Pydantic)
- **Core**: Configuración, database, autenticación JWT

### Frontend (Nuxt 4 + PrimeVue)

```
Pages → Composables → Stores (Pinia)
  ↓           ↓
Components   Utils
```

## 🛠️ Stack Tecnológico

### Backend
- **Framework**: FastAPI 0.129.x
- **ORM**: SQLAlchemy 2.0.x
- **Validación**: Pydantic 2.x
- **Base de datos**: PostgreSQL (psycopg2-binary)
- **Autenticación**: JWT (PyJWT) + Passlib[bcrypt]
- **Server**: Uvicorn 0.41.x (desarrollo) / Mangum 0.21.x (AWS Lambda)
- **Python**: 3.12+
- **Health Check**: Verificación de estado de BD incluida

### Frontend
- **Framework**: Nuxt 4.3.x
- **UI Library**: PrimeVue 4.5.x
- **Estilos**: Tailwind CSS 4.x + TailwindCSS PrimeUI
- **Iconos**: @iconify/json + @iconify/tailwind4
- **Estado**: Pinia 3.x
- **PWA**: @vite-pwa/nuxt
- **TypeScript**: Soporte completo
- **Navegación**: Sidebar desktop fijo + barra inferior mobile + drawer con overlay (PrimeVue Drawer)

### DevOps & Deployment
- **Backend**: AWS SAM + Lambda
- **Frontend**: Cloudflare Workers (Wrangler)
- **Package Manager Backend**: Poetry
- **Package Manager Frontend**: npm

## 📁 Estructura del Proyecto

```
mvp-base/
├── back/                      # Backend (FastAPI)
│   ├── src/
│   │   ├── core/             # Configuración, base de datos y auth
│   │   │   ├── config.py     # Settings (env vars, JWT, etc)
│   │   │   ├── database.py   # Database connection
│   │   │   ├── auth.py       # JWT & password hashing
│   │   │   └── __init__.py
│   │   ├── models/           # SQLAlchemy models
│   │   ├── repositories/     # Data access layer
│   │   ├── routes/           # API endpoints
│   │   ├── schemas/          # Pydantic schemas (DTOs)
│   │   ├── services/         # Business logic
│   │   └── main.py           # FastAPI app
│   ├── sql/                  # Scripts SQL
│   ├── lambda_handler.py     # AWS Lambda handler
│   ├── pyproject.toml        # Poetry dependencies
│   ├── requirements.txt      # Pip dependencies
│   ├── samconfig.toml        # SAM configuration
│   ├── template.yaml         # SAM/CloudFormation template
│   ├── deploy.sh             # Deployment script
│   └── README.md
│
├── front/                     # Frontend (Nuxt)
│   ├── app/
│   │   ├── assets/
│   │   │   ├── css/
│   │   │   │   └── main.css        # Tailwind imports
│   │   │   └── themes/
│   │   │       └── theme.js        # PrimeVue theme
│   │   ├── components/
│   │   │   ├── AppHeader.vue       # Header global (avatar, menú usuario)
│   │   │   └── AppNavigation.vue   # Sidebar desktop + barra mobile + drawer
│   │   ├── layouts/
│   │   │   └── default.vue         # Layout principal (header + nav + slot)
│   │   └── pages/
│   │       ├── index.vue           # Landing page
│   │       ├── demo.vue            # Demo de componentes
│   │       └── docs.vue            # Documentación del template
│   ├── nuxt.config.ts              # Nuxt configuration
│   ├── tailwind.config.js          # Tailwind configuration
│   ├── package.json
│   └── README.md
│
├── .gitignore
└── README.md                  # Este archivo
```

## 📋 Requisitos

### Backend
- Python 3.12 o superior
- PostgreSQL 14+
- Poetry (opcional) o pip

### Frontend
- Node.js 18+ / Bun
- npm, pnpm, yarn o bun

### Despliegue
- AWS CLI + SAM CLI (para backend)
- Wrangler CLI (para frontend)

## 🚀 Instalación

### 1. Usar como Template

**Opción A: Desde GitHub (Recomendado)**
1. Click en "Use this template" → "Create a new repository"
2. Clona tu nuevo repositorio
3. Ejecuta el script de setup:

```bash
git clone <tu-nuevo-repo-url>
cd <tu-proyecto>
./setup-project.sh
```

**Opción B: Clone directo**
```bash
git clone <repository-url>
cd mvp-base
./setup-project.sh
```

El script `setup-project.sh` te preguntará:
- Nombre del proyecto
- Descripción
- Autor y email
- Y configurará automáticamente todos los archivos

### 2. Backend Setup

```bash
cd back

# Con Poetry (recomendado)
poetry install

# O con pip
pip install -r requirements.txt
```

**Configurar variables de entorno:**

```bash
# Copiar archivo de ejemplo
cp back/.env.example back/.env

# Editar back/.env con tus valores reales
# Especialmente DATABASE_URL y JWT_SECRET_KEY
```

Variables en `back/.env`:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/mvp_base

# Application
DEBUG=True

# JWT (se genera automáticamente con setup-project.sh)
JWT_SECRET_KEY=your-super-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=10080
```

### 3. Frontend Setup

```bash
cd front

# Instalar dependencias
npm install
# o
pnpm install
# o
yarn install
# o
bun install
```

## 💻 Desarrollo

### Backend

```bash
cd back

# Iniciar servidor de desarrollo
uvicorn src.main:app --reload --port 8000

# Con Poetry
poetry run uvicorn src.main:app --reload --port 8000
```

API disponible en: `http://localhost:8000`
Docs interactiva: `http://localhost:8000/docs`
Health check: `http://localhost:8000/health`

**Endpoints de autenticación:**

```bash
# Registrar usuario (Form Data)
POST /auth/register
Content-Type: multipart/form-data
  email: user@example.com
  password: secreto123
  name: Juan Pérez

# Login (Form Data)
POST /auth/login
Content-Type: multipart/form-data
  email: user@example.com
  password: secreto123

# Obtener usuario actual (requiere token)
GET /auth/me
Authorization: Bearer <token>
```

**Verificar estado:**

```bash
# Health check con estado de base de datos
curl http://localhost:8000/health

# Respuesta:
{
  "status": "healthy",        # o "degraded" si BD desconectada
  "service": "MVP Base API",
  "version": "1.0.0",
  "database": "connected"     # o "disconnected"
}
```

### Frontend

```bash
cd front

# Iniciar servidor de desarrollo
npm run dev

# O con otros package managers
pnpm dev
yarn dev
bun run dev
```

App disponible en: `http://localhost:3000`

## 🚢 Despliegue

### Backend (AWS Lambda)

**Prerrequisitos:**
- AWS CLI configurado
- AWS SAM CLI instalado

**Desplegar:**

```bash
cd back

# Build y deploy
sam build
sam deploy --guided

# O usar el script
./deploy.sh
```

**Configurar variables en template.yaml** antes del despliegue:
- `DATABASE_URL`: Connection string de PostgreSQL
- `JWT_SECRET_KEY`: Secret key para JWT
- `DEBUG`: false en producción

### Frontend (Cloudflare Workers)

**Prerrequisitos:**
- Wrangler CLI instalado y autenticado

**Desplegar:**

```bash
cd front

# Build y deploy
npm run deploy

# O manualmente
npm run build
wrangler deploy .output/server/index.mjs --assets .output/public
```

**Preview local:**

```bash
npm run preview
```

## ⚙️ Configuración

### Backend Configuration

Archivo: `back/src/core/config.py`

```python
class Settings(BaseSettings):
    # Database
    DATABASE_URL: str

    # Application
    DEBUG: bool

    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 días
```

### Frontend Configuration

Archivo: `front/nuxt.config.ts`

```typescript
export default defineNuxtConfig({
  modules: [
    '@primevue/nuxt-module',
    '@pinia/nuxt',
  ],

  primevue: {
    importTheme: { from: '~/assets/themes/theme.js' },
  },

  // ... más configuración
})
```

## 📝 Convenciones de Código

### Backend (Python)
- PEP 8 style guide
- Type hints en funciones
- Docstrings en clases y funciones públicas
- Nombres descriptivos en snake_case

### Frontend (TypeScript)
- ESLint + Prettier
- Composables para lógica reutilizable
- Componentes SFC (Single File Components)
- camelCase para variables, PascalCase para componentes

## 🔐 Seguridad

- ✅ Autenticación JWT
- ✅ Hash de contraseñas con bcrypt
- ✅ Validación de entrada con Pydantic
- ✅ Variables de entorno para secrets
- ⚠️ **IMPORTANTE**: Cambiar `JWT_SECRET_KEY` en producción

## 📄 Licencia

ISC

## 👤 Autor

**Edinson Mendoza**
- Email: emmendoza2794@gmail.com

---

**Nota**: Este es un proyecto base. Personaliza según tus necesidades específicas.
