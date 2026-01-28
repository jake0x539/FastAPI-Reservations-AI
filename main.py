from contextlib import asynccontextmanager
from typing import List
from fastapi import FastAPI, HTTPException
from models import Reservation, ReservationCreate, Customer, CustomerCreate
import database


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup."""
    database.initialize_rooms()
    yield


app = FastAPI(title="Conference Room Reservation API", lifespan=lifespan)


@app.post("/reservations", response_model=Reservation, status_code=201)
def create_reservation(reservation_data: ReservationCreate):
    """
    Create a new reservation for a conference room.

    Validates:
    - Customer and room exist
    - Start time is not in the past
    - Start time is before end time (handled by Pydantic validation)
    - No time conflicts with existing reservations
    """
    # Check if customer exists
    customer = database.get_customer(reservation_data.customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail=f"Customer with id {reservation_data.customer_id} not found")

    # Check if room exists
    room = database.get_room(reservation_data.room_id)
    if not room:
        raise HTTPException(status_code=404, detail=f"Room with id {reservation_data.room_id} not found")

    # Check if start time is in the past
    if database.check_past_reservation(reservation_data.start_time):
        raise HTTPException(status_code=400, detail="Cannot create reservations in the past")

    # Check for time conflicts
    if database.check_time_conflict(reservation_data.room_id, reservation_data.start_time, reservation_data.end_time):
        raise HTTPException(status_code=409, detail="Time conflict: Room is already reserved for this time period")

    # Create the reservation
    reservation = database.create_reservation(
        customer_id=reservation_data.customer_id,
        room_id=reservation_data.room_id,
        start_time=reservation_data.start_time,
        end_time=reservation_data.end_time
    )

    return reservation


@app.delete("/reservations/{reservation_id}", status_code=204)
def delete_reservation(reservation_id: int):
    """Delete a reservation by ID."""
    if not database.delete_reservation(reservation_id):
        raise HTTPException(status_code=404, detail=f"Reservation with id {reservation_id} not found")


@app.get("/rooms/{room_id}/reservations", response_model=List[Reservation])
def get_room_reservations(room_id: int):
    """Get all reservations for a specific room."""
    # Check if room exists
    room = database.get_room(room_id)
    if not room:
        raise HTTPException(status_code=404, detail=f"Room with id {room_id} not found")

    return database.get_reservations_for_room(room_id)


@app.get("/rooms", response_model=List[dict])
def list_rooms():
    """List all available rooms."""
    return [{"id": room.id, "name": room.name} for room in database.rooms]


@app.post("/customers", response_model=Customer, status_code=201)
def create_customer(customer_data: CustomerCreate):
    """Create a new customer."""
    return database.create_customer(name=customer_data.name, email=customer_data.email)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
