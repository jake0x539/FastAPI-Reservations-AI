# Frontend Integration Guide

This guide provides information for frontend developers integrating with the Conference Room Reservation API.

## CORS Configuration

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

## DateTime Handling

All datetime fields must be:
- **Timezone-aware** (must include timezone information)
- **ISO 8601 format** with timezone suffix (e.g., `Z` for UTC or `+00:00`)

**Important**: The API does **not** automatically convert timezones to UTC. It accepts any timezone-aware datetime and preserves it as-is. However, it's recommended to use UTC for consistency.

### JavaScript Example (UTC recommended)

```javascript
const startTime = new Date().toISOString();  // "2026-01-30T14:00:00.000Z"
```

### Python Example (UTC recommended)

```python
from datetime import datetime, timezone

start_time = datetime.now(timezone.utc).isoformat()  # "2026-01-30T14:00:00+00:00"
```

### The API will reject timezone-naive datetimes

```javascript
// ❌ This will fail (no timezone)
"2026-01-30T14:00:00"

// ✅ This will work (UTC timezone)
"2026-01-30T14:00:00Z"

// ✅ This will also work (explicit timezone)
"2026-01-30T14:00:00+05:00"
```

## Error Handling

The API returns standard HTTP status codes with detailed error messages in the response body:

```json
{
  "detail": "Customer with email 'john@example.com' already exists"
}
```

### Status Codes

- `200`: Success
- `201`: Resource created
- `204`: Success with no content
- `400`: Bad request (validation error)
- `404`: Resource not found
- `409`: Conflict (duplicate or time conflict)
- `422`: Unprocessable entity (invalid data format)

## Example Requests

### Using Fetch API

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

// List all rooms
const listRooms = async () => {
  const response = await fetch('http://localhost:8000/rooms');

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail);
  }

  return await response.json();
};

// Delete a reservation
const deleteReservation = async (reservationId) => {
  const response = await fetch(`http://localhost:8000/reservations/${reservationId}`, {
    method: 'DELETE'
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail);
  }
};
```

### Using Axios

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

// Get room reservations
const getRoomReservations = async (roomId) => {
  try {
    const response = await api.get(`/rooms/${roomId}/reservations`);
    return response.data;
  } catch (error) {
    console.error('Error fetching reservations:', error.response.data.detail);
    throw error;
  }
};

// List all rooms
const listRooms = async () => {
  try {
    const response = await api.get('/rooms');
    return response.data;
  } catch (error) {
    console.error('Error fetching rooms:', error.response.data.detail);
    throw error;
  }
};

// Delete a reservation
const deleteReservation = async (reservationId) => {
  try {
    await api.delete(`/reservations/${reservationId}`);
  } catch (error) {
    console.error('Error deleting reservation:', error.response.data.detail);
    throw error;
  }
};
```

## TypeScript Types

If you're using TypeScript, here are the type definitions:

```typescript
interface Customer {
  id: number;
  name: string;
  email: string;
}

interface Room {
  id: number;
  name: string;
}

interface Reservation {
  id: number;
  customer_id: number;
  room_id: number;
  start_time: string;
  end_time: string;
}

interface CustomerCreate {
  name: string;
  email: string;
}

interface ReservationCreate {
  customer_id: number;
  room_id: number;
  start_time: string;
  end_time: string;
}

interface ApiError {
  detail: string;
}
```
