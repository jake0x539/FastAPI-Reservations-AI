# API Documentation

## Base URL

```
http://localhost:8000
```

## Interactive Documentation

FastAPI provides automatic interactive API documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Endpoints

### List Rooms

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

### Create Customer

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

### Create Reservation

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

### Delete Reservation

```http
DELETE /reservations/{reservation_id}
```

**Response:** `204 No Content`

**Error Responses:**
- `404 Not Found`: Reservation doesn't exist

---

### Get Room Reservations

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

## Data Models

### Customer
```typescript
{
  id: number;
  name: string;
  email: string;
}
```

### Room
```typescript
{
  id: number;
  name: string;
}
```

### Reservation
```typescript
{
  id: number;
  customer_id: number;
  room_id: number;
  start_time: string;  // ISO 8601 datetime with timezone
  end_time: string;    // ISO 8601 datetime with timezone
}
```

## HTTP Status Codes

- `200`: Success
- `201`: Resource created
- `204`: Success with no content
- `400`: Bad request (validation error)
- `404`: Resource not found
- `409`: Conflict (duplicate or time conflict)
- `422`: Unprocessable entity (invalid data format)
