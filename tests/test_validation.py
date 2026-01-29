import pytest
from datetime import datetime, timezone, timedelta
from fastapi import HTTPException
from src.models import ReservationCreate, CustomerCreate
from src import database
from src import validation


@pytest.fixture(autouse=True)
def reset_database():
    """Reset database before each test."""
    database.customers.clear()
    database.rooms.clear()
    database.reservations.clear()
    database._next_customer_id = 1
    database._next_room_id = 1
    database._next_reservation_id = 1
    database.initialize_rooms()
    yield


def test_validate_reservation_customer_not_found():
    """Test validation fails when customer doesn't exist."""
    start = datetime.now(timezone.utc) + timedelta(hours=1)
    end = start + timedelta(hours=2)

    reservation_data = ReservationCreate(
        customer_id=999,
        room_id=1,
        start_time=start,
        end_time=end
    )

    with pytest.raises(HTTPException) as exc_info:
        validation.validate_reservation(reservation_data)

    assert exc_info.value.status_code == 404
    assert "Customer with id 999 not found" in exc_info.value.detail


def test_validate_reservation_room_not_found():
    """Test validation fails when room doesn't exist."""
    database.create_customer("John Doe", "john@example.com")

    start = datetime.now(timezone.utc) + timedelta(hours=1)
    end = start + timedelta(hours=2)

    reservation_data = ReservationCreate(
        customer_id=1,
        room_id=999,
        start_time=start,
        end_time=end
    )

    with pytest.raises(HTTPException) as exc_info:
        validation.validate_reservation(reservation_data)

    assert exc_info.value.status_code == 404
    assert "Room with id 999 not found" in exc_info.value.detail


def test_validate_reservation_past_time():
    """Test validation fails when start time is in the past."""
    database.create_customer("John Doe", "john@example.com")

    start = datetime.now(timezone.utc) - timedelta(hours=2)
    end = start + timedelta(hours=2)

    reservation_data = ReservationCreate(
        customer_id=1,
        room_id=1,
        start_time=start,
        end_time=end
    )

    with pytest.raises(HTTPException) as exc_info:
        validation.validate_reservation(reservation_data)

    assert exc_info.value.status_code == 422
    assert "Cannot create reservations in the past" in exc_info.value.detail


def test_validate_reservation_time_conflict():
    """Test validation fails when there's a time conflict."""
    database.create_customer("John Doe", "john@example.com")

    # Create existing reservation
    start1 = datetime.now(timezone.utc) + timedelta(hours=1)
    end1 = start1 + timedelta(hours=2)
    database.create_reservation(1, 1, start1, end1)

    # Try to create overlapping reservation
    start2 = start1 + timedelta(minutes=30)
    end2 = end1 + timedelta(minutes=30)

    reservation_data = ReservationCreate(
        customer_id=1,
        room_id=1,
        start_time=start2,
        end_time=end2
    )

    with pytest.raises(HTTPException) as exc_info:
        validation.validate_reservation(reservation_data)

    assert exc_info.value.status_code == 409
    assert "Time conflict" in exc_info.value.detail


def test_validate_reservation_success():
    """Test validation succeeds with valid data."""
    database.create_customer("John Doe", "john@example.com")

    start = datetime.now(timezone.utc) + timedelta(hours=1)
    end = start + timedelta(hours=2)

    reservation_data = ReservationCreate(
        customer_id=1,
        room_id=1,
        start_time=start,
        end_time=end
    )

    # Should not raise an exception
    validation.validate_reservation(reservation_data)


def test_validate_room_exists():
    """Test room exists validation."""
    # Should not raise for existing room
    validation.validate_room_exists(1)

    # Should raise for non-existent room
    with pytest.raises(HTTPException) as exc_info:
        validation.validate_room_exists(999)

    assert exc_info.value.status_code == 404
    assert "Room with id 999 not found" in exc_info.value.detail


def test_validate_reservation_exists():
    """Test reservation exists validation."""
    database.create_customer("John Doe", "john@example.com")

    start = datetime.now(timezone.utc) + timedelta(hours=1)
    end = start + timedelta(hours=2)
    database.create_reservation(1, 1, start, end)

    # Should not raise for existing reservation
    validation.validate_reservation_exists(1)
    assert len(database.reservations) == 1

    # Should raise for non-existent reservation
    with pytest.raises(HTTPException) as exc_info:
        validation.validate_reservation_exists(999)

    assert exc_info.value.status_code == 404
    assert "Reservation with id 999 not found" in exc_info.value.detail


def test_validate_customer_unique_email():
    """Test customer email uniqueness validation."""
    database.create_customer("John Doe", "john@example.com")

    # Try to create customer with duplicate email
    customer_data = CustomerCreate(
        name="Jane Smith",
        email="john@example.com"
    )

    with pytest.raises(HTTPException) as exc_info:
        validation.validate_customer_unique(customer_data)

    assert exc_info.value.status_code == 409
    assert "email 'john@example.com' already exists" in exc_info.value.detail


def test_validate_customer_unique_name():
    """Test customer name uniqueness validation."""
    database.create_customer("John Doe", "john@example.com")

    # Try to create customer with duplicate name
    customer_data = CustomerCreate(
        name="John Doe",
        email="jane@example.com"
    )

    with pytest.raises(HTTPException) as exc_info:
        validation.validate_customer_unique(customer_data)

    assert exc_info.value.status_code == 409
    assert "name 'John Doe' already exists" in exc_info.value.detail


def test_validate_customer_unique_success():
    """Test customer uniqueness validation succeeds with unique data."""
    database.create_customer("John Doe", "john@example.com")

    customer_data = CustomerCreate(
        name="Jane Smith",
        email="jane@example.com"
    )

    # Should not raise an exception
    validation.validate_customer_unique(customer_data)
