"""FastAPI application for conference room reservation system."""

from contextlib import asynccontextmanager
from typing import List
from fastapi import FastAPI
from src.models import Reservation, ReservationCreate, Customer, CustomerCreate
from src import database
from src import validation


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup."""
    database.initialize_rooms()
    yield


app = FastAPI(title="Conference Room Reservation API", lifespan=lifespan)


@app.post("/reservations", response_model=Reservation, status_code=201)
def create_reservation(reservation_data: ReservationCreate):
    """Create a new reservation for a conference room."""
    validation.validate_reservation(reservation_data)

    return database.create_reservation(
        customer_id=reservation_data.customer_id,
        room_id=reservation_data.room_id,
        start_time=reservation_data.start_time,
        end_time=reservation_data.end_time
    )


@app.delete("/reservations/{reservation_id}", status_code=204)
def delete_reservation(reservation_id: int):
    """Delete a reservation by ID."""
    validation.validate_reservation_exists(reservation_id)
    database.delete_reservation(reservation_id)


@app.get("/rooms/{room_id}/reservations", response_model=List[Reservation])
def get_room_reservations(room_id: int):
    """Get all reservations for a specific room."""
    validation.validate_room_exists(room_id)
    return database.get_reservations_for_room(room_id)


@app.get("/rooms", response_model=List[dict])
def list_rooms():
    """List all available rooms."""
    return [{"id": room.id, "name": room.name} for room in database.rooms]


@app.post("/customers", response_model=Customer, status_code=201)
def create_customer(customer_data: CustomerCreate):
    """Create a new customer."""
    validation.validate_customer_unique(customer_data)
    return database.create_customer(name=customer_data.name, email=customer_data.email)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
