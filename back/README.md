# Backend - MVP Base

Backend structure following layered architecture principles.

## Structure

```
back/
├── src/
│   ├── core/          # Core functionality (config, database, auth)
│   │   ├── config.py  # Settings and configuration
│   │   ├── database.py # Database connection
│   │   └── auth.py    # JWT authentication & password hashing
│   ├── models/        # Database models
│   ├── repositories/  # Data access layer
│   ├── routes/        # API endpoints
│   ├── schemas/       # Pydantic schemas (DTOs)
│   └── services/      # Business logic
├── sql/               # SQL scripts
├── lambda_handler.py  # AWS Lambda handler
├── pyproject.toml     # Project configuration
├── requirements.txt   # Python dependencies
├── samconfig.toml     # SAM configuration
└── template.yaml      # SAM template
```

## Layers

- **Routes**: HTTP endpoints and request/response handling
- **Services**: Business logic
- **Repositories**: Data access and database operations
- **Models**: Database entity definitions
- **Schemas**: Data validation and serialization
- **Core**: Shared utilities and configuration
