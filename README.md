# Conference Room Reservation API

A FastAPI-based REST API for managing conference room reservations with time conflict detection and validation.

## Table of Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [Getting Started](#getting-started)
  - [Docker Deployment (Recommended)](#docker-deployment-recommended)
  - [Local Development](#local-development)
- [Running Tests](#running-tests)
- [Documentation](#documentation)
- [Project Structure](#project-structure)

## Features

- **Room Management**: List all available conference rooms
- **Customer Management**: Create customers with unique email and name validation
- **Reservation System**: Create, delete, and view reservations
- **Time Conflict Detection**: Prevents overlapping reservations for the same room
- **Validation**:
  - No reservations in the past
  - Start time must be before end time
  - Timezone-aware datetime handling (UTC)
  - Unique customer emails and names

## Technology Stack

- **Python 3.13+**
- **FastAPI**: Modern web framework for building APIs
- **Pydantic**: Data validation using Python type annotations
- **uvicorn**: ASGI server
- **pytest**: Testing framework
- **Docker**: Containerization
- **uv**: Fast Python package installer and resolver

## Getting Started

### Docker Deployment (Recommended)

1. **Build and run the container:**
   ```bash
   docker-compose up --build
   ```

2. **Access the API:**
   - API: http://localhost:8000
   - Interactive API docs: http://localhost:8000/docs
   - Alternative API docs: http://localhost:8000/redoc

3. **Stop the container:**
   ```bash
   docker-compose down
   ```

### Local Development

1. **Prerequisites:**
   - Python 3.13 or higher
   - [uv](https://github.com/astral-sh/uv) package manager

2. **Install dependencies:**
   ```bash
   uv sync
   ```

3. **Run the application:**
   ```bash
   uv run python main.py
   ```

4. **Access the API:**
   - API: http://localhost:8000
   - Interactive API docs: http://localhost:8000/docs
   - Alternative API docs: http://localhost:8000/redoc

## Running Tests

The project includes comprehensive unit and integration tests.

**Run all tests:**
```bash
uv run pytest
```

**Run tests with verbose output:**
```bash
uv run pytest -v
```

**Run specific test file:**
```bash
uv run pytest test_api.py
```

**Test Coverage:**
- 40 tests total
- Unit tests for database operations
- Unit tests for validation logic
- Integration tests for all API endpoints

## Documentation

- **[API Documentation](docs/API_DOCUMENTATION.md)** - Complete API reference with all endpoints, request/response formats, and data models
- **[Frontend Integration Guide](docs/FRONTEND_INTEGRATION.md)** - Guide for integrating the API with frontend applications, including CORS setup, datetime handling, error handling, and code examples

## Project Structure

```
fastapi-reservations-ai/
├── src/
│   ├── __init__.py             # Package initialization
│   ├── models.py               # Pydantic models for data validation
│   ├── database.py             # In-memory database and CRUD operations
│   └── validation.py           # Business logic validation
├── tests/
│   ├── test_api.py             # Integration tests for API endpoints
│   ├── test_database.py        # Unit tests for database functions
│   └── test_validation.py      # Unit tests for validation logic
├── docs/
│   ├── API_DOCUMENTATION.md    # Complete API reference
│   └── FRONTEND_INTEGRATION.md # Frontend integration guide
├── main.py                     # FastAPI application and endpoints
├── conftest.py                 # Pytest configuration
├── Dockerfile                  # Docker container configuration
├── docker-compose.yml          # Docker Compose orchestration
├── .dockerignore               # Docker build exclusions
├── pyproject.toml              # Project dependencies and configuration
└── README.md                   # This file
```

**Note**: This application uses an in-memory database. All data (customers, reservations) will be lost when the application restarts. This is suitable for demonstration and testing purposes.
