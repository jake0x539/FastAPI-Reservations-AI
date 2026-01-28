# Conference Room Reservation API

A FastAPI-based REST API for managing conference room reservations with time conflict detection and validation.

## Table of Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [Getting Started](#getting-started)
  - [Docker Deployment (Recommended)](#docker-deployment-recommended)
  - [Local Development](#local-development)
- [API Documentation](#api-documentation)
  - [Base URL](#base-url)
  - [Endpoints](#endpoints)
  - [Data Models](#data-models)
- [Running Tests](#running-tests)
- [Frontend Integration Guide](#frontend-integration-guide)
  - [CORS Configuration](#cors-configuration)
  - [DateTime Handling](#datetime-handling)
  - [Error Handling](#error-handling)
  - [Example Requests](#example-requests)
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

## API Documentation

### Base URL

```
http://localhost:8000
```

### Endpoints

#### List Rooms

```http
GET /rooms
```

Returns all available conference rooms.

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "name": "Conference Room A"
  }
]
```

---

#### Create Customer

```http
POST /customers
```

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john@example.com"
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com"
}
```

**Error Responses:**
- `409 Conflict`: Email or name already exists
- `422 Unprocessable Entity`: Invalid email format

---

#### Create Reservation

```http
POST /reservations
```

**Request Body:**
```json
{
  "customer_id": 1,
  "room_id": 1,
  "start_time": "2026-01-30T14:00:00Z",
  "end_time": "2026-01-30T16:00:00Z"
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "customer_id": 1,
  "room_id": 1,
  "start_time": "2026-01-30T14:00:00Z",
  "end_time": "2026-01-30T16:00:00Z"
}
```

**Error Responses:**
- `400 Bad Request`: Reservation in the past
- `404 Not Found`: Customer or room doesn't exist
- `409 Conflict`: Time conflict with existing reservation
- `422 Unprocessable Entity`: Invalid datetime format or end_time before start_time

---

#### Delete Reservation

```http
DELETE /reservations/{reservation_id}
```

**Response:** `204 No Content`

**Error Responses:**
- `404 Not Found`: Reservation doesn't exist

---

#### Get Room Reservations

```http
GET /rooms/{room_id}/reservations
```

Returns all reservations for a specific room.

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "customer_id": 1,
    "room_id": 1,
    "start_time": "2026-01-30T14:00:00Z",
    "end_time": "2026-01-30T16:00:00Z"
  }
]
```

**Error Responses:**
- `404 Not Found`: Room doesn't exist

---

### Data Models

#### Customer
```typescript
{
  id: number;
  name: string;
  email: string;
}
```

#### Room
```typescript
{
  id: number;
  name: string;
}
```

#### Reservation
```typescript
{
  id: number;
  customer_id: number;
  room_id: number;
  start_time: string;  // ISO 8601 datetime with timezone
  end_time: string;    // ISO 8601 datetime with timezone
}
```

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

## Frontend Integration Guide

### CORS Configuration

The API currently does not include CORS middleware. If you need to access the API from a frontend application running on a different origin, you'll need to add CORS support.

Add this to `main.py`:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### DateTime Handling

All datetime fields must be:
- **Timezone-aware** (must include timezone information)
- **ISO 8601 format** with timezone suffix (e.g., `Z` for UTC or `+00:00`)

**Important**: The API does **not** automatically convert timezones to UTC. It accepts any timezone-aware datetime and preserves it as-is. However, it's recommended to use UTC for consistency.

**JavaScript Example (UTC recommended):**
```javascript
const startTime = new Date().toISOString();  // "2026-01-30T14:00:00.000Z"
```

**Python Example (UTC recommended):**
```python
from datetime import datetime, timezone

start_time = datetime.now(timezone.utc).isoformat()  # "2026-01-30T14:00:00+00:00"
```

**The API will reject timezone-naive datetimes:**
```javascript
// ❌ This will fail (no timezone)
"2026-01-30T14:00:00"

// ✅ This will work (UTC timezone)
"2026-01-30T14:00:00Z"

// ✅ This will also work (explicit timezone)
"2026-01-30T14:00:00+05:00"
```

### Error Handling

The API returns standard HTTP status codes with detailed error messages in the response body:

```json
{
  "detail": "Customer with email 'john@example.com' already exists"
}
```

**Status Codes:**
- `200`: Success
- `201`: Resource created
- `204`: Success with no content
- `400`: Bad request (validation error)
- `404`: Resource not found
- `409`: Conflict (duplicate or time conflict)
- `422`: Unprocessable entity (invalid data format)

### Example Requests

**Using Fetch API:**

```javascript
// Create a customer
const createCustomer = async () => {
  const response = await fetch('http://localhost:8000/customers', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      name: 'John Doe',
      email: 'john@example.com'
    })
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail);
  }

  return await response.json();
};

// Create a reservation
const createReservation = async (customerId, roomId) => {
  const now = new Date();
  const startTime = new Date(now.getTime() + 3600000); // 1 hour from now
  const endTime = new Date(startTime.getTime() + 7200000); // 2 hours later

  const response = await fetch('http://localhost:8000/reservations', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      customer_id: customerId,
      room_id: roomId,
      start_time: startTime.toISOString(),
      end_time: endTime.toISOString()
    })
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail);
  }

  return await response.json();
};

// Get room reservations
const getRoomReservations = async (roomId) => {
  const response = await fetch(`http://localhost:8000/rooms/${roomId}/reservations`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail);
  }

  return await response.json();
};
```

**Using Axios:**

```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json'
  }
});

// Create a customer
const createCustomer = async (name, email) => {
  try {
    const response = await api.post('/customers', { name, email });
    return response.data;
  } catch (error) {
    console.error('Error creating customer:', error.response.data.detail);
    throw error;
  }
};

// Create a reservation
const createReservation = async (customerId, roomId, startTime, endTime) => {
  try {
    const response = await api.post('/reservations', {
      customer_id: customerId,
      room_id: roomId,
      start_time: startTime,
      end_time: endTime
    });
    return response.data;
  } catch (error) {
    console.error('Error creating reservation:', error.response.data.detail);
    throw error;
  }
};
```

## Project Structure

```
fastapi-reservations-ai/
├── models.py              # Pydantic models for data validation
├── database.py            # In-memory database and CRUD operations
├── validation.py          # Business logic validation
├── main.py                # FastAPI application and endpoints
├── test_api.py            # Integration tests for API endpoints
├── test_database.py       # Unit tests for database functions
├── test_validation.py     # Unit tests for validation logic
├── Dockerfile             # Docker container configuration
├── docker-compose.yml     # Docker Compose orchestration
├── .dockerignore          # Docker build exclusions
├── pyproject.toml         # Project dependencies and configuration
└── README.md              # This file
```

**Note**: This application uses an in-memory database. All data (customers, reservations) will be lost when the application restarts. This is suitable for demonstration and testing purposes.
