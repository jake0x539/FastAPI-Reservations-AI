from datetime import datetime, timezone
from typing import List, Optional
from models import Customer, Room, Reservation


# In-memory storage
customers: List[Customer] = []
rooms: List[Room] = []
reservations: List[Reservation] = []

# ID counters
_next_customer_id = 1
_next_room_id = 1
_next_reservation_id = 1


def initialize_rooms() -> None:
    """Initialize the database with 5 dummy rooms."""
    global _next_room_id
    dummy_rooms = [
        Room(id=1, name="Conference Room A"),
        Room(id=2, name="Conference Room B"),
        Room(id=3, name="Meeting Room 1"),
        Room(id=4, name="Meeting Room 2"),
        Room(id=5, name="Executive Boardroom"),
    ]
    rooms.extend(dummy_rooms)
    _next_room_id = 6


def get_room(room_id: int) -> Optional[Room]:
    """Get a room by ID."""
    return next((room for room in rooms if room.id == room_id), None)


def get_customer(customer_id: int) -> Optional[Customer]:
    """Get a customer by ID."""
    return next((customer for customer in customers if customer.id == customer_id), None)


def get_reservation(reservation_id: int) -> Optional[Reservation]:
    """Get a reservation by ID."""
    return next((res for res in reservations if res.id == reservation_id), None)


def get_reservations_for_room(room_id: int) -> List[Reservation]:
    """Get all reservations for a specific room."""
    return [res for res in reservations if res.room_id == room_id]


def check_time_conflict(room_id: int, start_time: datetime, end_time: datetime, exclude_reservation_id: Optional[int] = None) -> bool:
    """
    Check if a time period conflicts with existing reservations for a room.
    Returns True if there is a conflict, False otherwise.
    """
    room_reservations = [
        res for res in reservations
        if res.room_id == room_id and (exclude_reservation_id is None or res.id != exclude_reservation_id)
    ]

    for reservation in room_reservations:
        # Check for any overlap: new_start < existing_end AND new_end > existing_start
        if start_time < reservation.end_time and end_time > reservation.start_time:
            return True

    return False


def check_past_reservation(start_time: datetime) -> bool:
    """
    Check if the start time is in the past.
    Returns True if it's in the past, False otherwise.
    """
    now = datetime.now(timezone.utc)
    return start_time < now


def create_reservation(customer_id: int, room_id: int, start_time: datetime, end_time: datetime) -> Reservation:
    """Create a new reservation."""
    global _next_reservation_id

    reservation = Reservation(
        id=_next_reservation_id,
        customer_id=customer_id,
        room_id=room_id,
        start_time=start_time,
        end_time=end_time
    )
    reservations.append(reservation)
    _next_reservation_id += 1

    return reservation


def delete_reservation(reservation_id: int) -> bool:
    """
    Delete a reservation by ID.
    Returns True if deleted, False if not found.
    """
    global reservations
    initial_length = len(reservations)
    reservations = [res for res in reservations if res.id != reservation_id]
    return len(reservations) < initial_length


def check_customer_email_exists(email: str) -> bool:
    """
    Check if a customer with the given email already exists.
    Returns True if email exists, False otherwise.
    """
    return any(customer.email == email for customer in customers)


def check_customer_name_exists(name: str) -> bool:
    """
    Check if a customer with the given name already exists.
    Returns True if name exists, False otherwise.
    """
    return any(customer.name == name for customer in customers)


def create_customer(name: str, email: str) -> Customer:
    """Create a new customer."""
    global _next_customer_id

    customer = Customer(
        id=_next_customer_id,
        name=name,
        email=email
    )
    customers.append(customer)
    _next_customer_id += 1

    return customer
