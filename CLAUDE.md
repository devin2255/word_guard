# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

御言(WordGuard) is a text content moderation system designed for User Generated Content (UGC). It provides intelligent filtering, blacklist/whitelist management, and multi-language text content risk classification using Domain-Driven Design (DDD) architecture.

**Tech Stack:**
- FastAPI (async web framework)
- Tortoise ORM (async ORM)  
- MySQL (database)
- Uvicorn (ASGI server)
- Python 3.7+
- DDD Architecture Pattern

## Development Commands

### Running the Application
```bash
# Development mode
python yuyan.py

# Production mode  
uvicorn src.main:app --host 0.0.0.0 --port 18000
```

### Testing
```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=src

# Run specific test file
pytest tests/unit/test_wordlist_entity.py
```

### Database Migrations
```bash
# Initialize migrations (first time only)
aerich init-db

# Generate new migration
aerich migrate

# Apply migrations
aerich upgrade
```

## Architecture Overview

### DDD Four-Layer Architecture
```
src/
├── domain/                    # Domain Layer (core business logic)
│   ├── wordlist/             # WordList aggregate
│   │   ├── entities/         # Domain entities
│   │   ├── value_objects/    # Value objects
│   │   ├── repositories/     # Repository interfaces
│   │   ├── services/         # Domain services
│   │   └── events/           # Domain events
│   └── app/                  # App aggregate
├── application/              # Application Layer (use case coordination)
│   ├── commands/             # Commands
│   ├── queries/              # Queries
│   ├── handlers/             # Command/Query handlers
│   └── dto/                  # Data Transfer Objects
├── infrastructure/           # Infrastructure Layer (technical implementation)
│   ├── repositories/         # Repository implementations
│   └── database/             # Database models (Tortoise ORM)
├── interfaces/               # Interface Layer (external interaction)
│   ├── controllers/          # Controllers
│   ├── routes/               # FastAPI routes
│   └── dependencies.py       # Dependency injection
├── shared/                   # Shared Kernel
│   ├── enums/                # Business enums
│   ├── exceptions/           # Domain exceptions
│   └── events/               # Event base classes
└── config/                   # Configuration
```

### Key Design Patterns

**Application Factory**: `src/main.py` contains `create_app()` function that:
- Initializes FastAPI application
- Registers routes from `src/interfaces/routes/`
- Sets up CORS middleware
- Configures database connections

**Domain-Driven Design**: 
- **Entities**: WordList, App with business rules and invariants
- **Value Objects**: ListName, RiskLevel for immutable concepts
- **Aggregates**: WordList as aggregate root
- **Repositories**: Abstract data access through interfaces
- **Domain Events**: WordListCreated, WordListUpdated

**CQRS Pattern**:
- Commands: CreateWordListCommand, UpdateWordListCommand
- Queries: GetWordListQuery, GetWordListsQuery  
- Handlers: Separate command and query processing

## Core Business Logic

### Enums (src/shared/enums/list_enums.py)
Key business enums defining system behavior:

- **ListType**: WHITELIST(0), IGNORELIST(1), BLACKLIST(2)
- **MatchRule**: TEXT_AND_NICKNAME(0), TEXT(1), NICKNAME(2), IP(3), ACCOUNT(4), ROLE_ID(5), DEVICE_FINGERPRINT(6)
- **RiskType**: Content risk classification (normal, political, pornographic, abusive, advertising, etc.)
- **Language**: 17+ supported languages
- **Status**: ENABLED(1), DISABLED(0)

### Domain Models
- **WordList**: Main entity for content filtering rules
- **App**: Application registry for multi-tenant support

### Soft Delete Pattern
All entities support soft deletion:
- Entities have `deleted_at` timestamps
- Repository implementations automatically filter deleted records
- Complete audit trail with created_by, updated_by, deleted_by fields

## Configuration

### Environment Configuration
- Settings loaded from `src/config/settings.py`
- Database configuration in `src/config/database.py`
- Aerich configuration in `src/config/aerich_config.py`

### Key Settings
- `DATABASE_URL`: MySQL connection string
- `APP_NAME`: Application display name
- `APP_ENV`: Environment identifier
- `DEBUG_MODE`: Development mode toggle

## API Routes

### WordList Management (/v1/wordlist)
- `POST /v1/wordlist` - Create wordlist
- `GET /v1/wordlist` - Get wordlist collection
- `GET /v1/wordlist/{id}` - Get wordlist by ID
- `PUT /v1/wordlist/{id}` - Update wordlist
- `DELETE /v1/wordlist/{id}` - Soft delete wordlist

### App Management (/v1/app)
- `POST /v1/app` - Create application
- `GET /v1/app` - Get application collection
- `GET /v1/app/by-id/{id}` - Get app by database ID
- `GET /v1/app/by-app-id/{app_id}` - Get app by application ID

## Important Notes

- All database operations use async/await with Tortoise ORM
- Entity field names use snake_case in database, camelCase in API responses
- Enum fields support both integer values and string descriptions
- System supports 17+ languages for international content moderation
- CORS configured to allow all origins (adjust for production)
- FastAPI auto-generates OpenAPI docs at `/docs`