from fastapi import HTTPException
from models import ReservationCreate
import database


def validate_reservation(reservation_data: ReservationCreate) -> None:
    """
    Validate a reservation request.

    Raises HTTPException if validation fails.
    """
    # Check if customer exists
    customer = database.get_customer(reservation_data.customer_id)
    if not customer:
        raise HTTPException(
            status_code=404,
            detail=f"Customer with id {reservation_data.customer_id} not found"
        )

    # Check if room exists
    room = database.get_room(reservation_data.room_id)
    if not room:
        raise HTTPException(
            status_code=404,
            detail=f"Room with id {reservation_data.room_id} not found"
        )

    # Check if start time is in the past
    if database.check_past_reservation(reservation_data.start_time):
        raise HTTPException(
            status_code=400,
            detail="Cannot create reservations in the past"
        )

    # Check for time conflicts
    if database.check_time_conflict(
        reservation_data.room_id,
        reservation_data.start_time,
        reservation_data.end_time
    ):
        raise HTTPException(
            status_code=409,
            detail="Time conflict: Room is already reserved for this time period"
        )


def validate_room_exists(room_id: int) -> None:
    """
    Validate that a room exists.

    Raises HTTPException if room not found.
    """
    room = database.get_room(room_id)
    if not room:
        raise HTTPException(
            status_code=404,
            detail=f"Room with id {room_id} not found"
        )


def validate_reservation_exists(reservation_id: int) -> None:
    """
    Validate that a reservation exists and delete it.

    Raises HTTPException if reservation not found.
    """
    if not database.delete_reservation(reservation_id):
        raise HTTPException(
            status_code=404,
            detail=f"Reservation with id {reservation_id} not found"
        )
