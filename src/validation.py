"""Validation logic for API endpoints."""

from fastapi import HTTPException
from src.models import ReservationCreate, CustomerCreate
from src import database


def validate_reservation(reservation_data: ReservationCreate) -> None:
    """
    Validate a reservation request.

    Raises HTTPException if validation fails.
    """
    customer = database.get_customer(reservation_data.customer_id)
    if not customer:
        raise HTTPException(
            status_code=404,
            detail=f"Customer with id {reservation_data.customer_id} not found"
        )

    room = database.get_room(reservation_data.room_id)
    if not room:
        raise HTTPException(
            status_code=404,
            detail=f"Room with id {reservation_data.room_id} not found"
        )

    if database.check_past_reservation(reservation_data.start_time):
        raise HTTPException(
            status_code=400,
            detail="Cannot create reservations in the past"
        )

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
    Validate that a reservation exists.

    Raises HTTPException if reservation not found.
    """
    reservation = database.get_reservation_by_id(reservation_id)
    if not reservation:
        raise HTTPException(
            status_code=404,
            detail=f"Reservation with id {reservation_id} not found"
        )


def validate_customer_unique(customer_data: CustomerCreate) -> None:
    """
    Validate that customer email and name are unique.

    Raises HTTPException if email or name already exists.
    """
    if database.check_customer_email_exists(customer_data.email):
        raise HTTPException(
            status_code=409,
            detail=f"Customer with email '{customer_data.email}' already exists"
        )

    if database.check_customer_name_exists(customer_data.name):
        raise HTTPException(
            status_code=409,
            detail=f"Customer with name '{customer_data.name}' already exists"
        )
