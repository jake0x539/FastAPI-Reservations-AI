import pytest
from datetime import datetime, timezone, timedelta
from models import Customer, Room, Reservation
import database


@pytest.fixture(autouse=True)
def reset_database():
    """Reset database before each test."""
    database.customers.clear()
    database.rooms.clear()
    database.reservations.clear()
    database._next_customer_id = 1
    database._next_room_id = 1
    database._next_reservation_id = 1
    yield


def test_initialize_rooms():
    """Test that rooms are initialized correctly."""
    database.initialize_rooms()
    assert len(database.rooms) == 5
    assert database.rooms[0].name == "Conference Room A"
    assert database.rooms[4].name == "Executive Boardroom"
    assert database._next_room_id == 6


def test_get_room():
    """Test getting a room by ID."""
    database.initialize_rooms()
    room = database.get_room(1)
    assert room is not None
    assert room.id == 1
    assert room.name == "Conference Room A"

    # Test non-existent room
    room = database.get_room(999)
    assert room is None


def test_create_customer():
    """Test creating a customer."""
    customer = database.create_customer("John Doe", "john@example.com")
    assert customer.id == 1
    assert customer.name == "John Doe"
    assert customer.email == "john@example.com"
    assert len(database.customers) == 1

    # Create another customer
    customer2 = database.create_customer("Jane Smith", "jane@example.com")
    assert customer2.id == 2
    assert len(database.customers) == 2


def test_get_customer():
    """Test getting a customer by ID."""
    database.create_customer("John Doe", "john@example.com")
    customer = database.get_customer(1)
    assert customer is not None
    assert customer.name == "John Doe"

    # Test non-existent customer
    customer = database.get_customer(999)
    assert customer is None


def test_check_customer_email_exists():
    """Test checking if customer email exists."""
    database.create_customer("John Doe", "john@example.com")
    assert database.check_customer_email_exists("john@example.com") is True
    assert database.check_customer_email_exists("nonexistent@example.com") is False


def test_check_customer_name_exists():
    """Test checking if customer name exists."""
    database.create_customer("John Doe", "john@example.com")
    assert database.check_customer_name_exists("John Doe") is True
    assert database.check_customer_name_exists("Jane Smith") is False


def test_create_reservation():
    """Test creating a reservation."""
    database.initialize_rooms()
    database.create_customer("John Doe", "john@example.com")

    start = datetime.now(timezone.utc) + timedelta(hours=1)
    end = start + timedelta(hours=2)

    reservation = database.create_reservation(1, 1, start, end)
    assert reservation.id == 1
    assert reservation.customer_id == 1
    assert reservation.room_id == 1
    assert reservation.start_time == start
    assert reservation.end_time == end
    assert len(database.reservations) == 1


def test_get_reservation():
    """Test getting a reservation by ID."""
    database.initialize_rooms()
    database.create_customer("John Doe", "john@example.com")

    start = datetime.now(timezone.utc) + timedelta(hours=1)
    end = start + timedelta(hours=2)

    database.create_reservation(1, 1, start, end)
    reservation = database.get_reservation(1)
    assert reservation is not None
    assert reservation.id == 1

    # Test non-existent reservation
    reservation = database.get_reservation(999)
    assert reservation is None


def test_delete_reservation():
    """Test deleting a reservation."""
    database.initialize_rooms()
    database.create_customer("John Doe", "john@example.com")

    start = datetime.now(timezone.utc) + timedelta(hours=1)
    end = start + timedelta(hours=2)

    database.create_reservation(1, 1, start, end)
    assert len(database.reservations) == 1

    # Delete the reservation
    result = database.delete_reservation(1)
    assert result is True
    assert len(database.reservations) == 0

    # Try to delete non-existent reservation
    result = database.delete_reservation(999)
    assert result is False


def test_get_reservations_for_room():
    """Test getting all reservations for a room."""
    database.initialize_rooms()
    database.create_customer("John Doe", "john@example.com")
    database.create_customer("Jane Smith", "jane@example.com")

    start1 = datetime.now(timezone.utc) + timedelta(hours=1)
    end1 = start1 + timedelta(hours=2)
    start2 = datetime.now(timezone.utc) + timedelta(hours=4)
    end2 = start2 + timedelta(hours=2)

    # Create reservations for room 1
    database.create_reservation(1, 1, start1, end1)
    database.create_reservation(2, 1, start2, end2)

    # Create reservation for room 2
    database.create_reservation(1, 2, start1, end1)

    room1_reservations = database.get_reservations_for_room(1)
    assert len(room1_reservations) == 2

    room2_reservations = database.get_reservations_for_room(2)
    assert len(room2_reservations) == 1


def test_check_past_reservation():
    """Test checking if a reservation is in the past."""
    past_time = datetime.now(timezone.utc) - timedelta(hours=1)
    future_time = datetime.now(timezone.utc) + timedelta(hours=1)

    assert database.check_past_reservation(past_time) is True
    assert database.check_past_reservation(future_time) is False


def test_check_time_conflict():
    """Test checking for time conflicts."""
    database.initialize_rooms()
    database.create_customer("John Doe", "john@example.com")

    # Create an existing reservation
    start1 = datetime.now(timezone.utc) + timedelta(hours=1)
    end1 = start1 + timedelta(hours=2)
    database.create_reservation(1, 1, start1, end1)

    # Test overlapping at the start
    overlap_start = start1 - timedelta(minutes=30)
    overlap_end = start1 + timedelta(minutes=30)
    assert database.check_time_conflict(1, overlap_start, overlap_end) is True

    # Test overlapping at the end
    overlap_start2 = end1 - timedelta(minutes=30)
    overlap_end2 = end1 + timedelta(minutes=30)
    assert database.check_time_conflict(1, overlap_start2, overlap_end2) is True

    # Test complete overlap (new reservation contains existing)
    overlap_start3 = start1 - timedelta(hours=1)
    overlap_end3 = end1 + timedelta(hours=1)
    assert database.check_time_conflict(1, overlap_start3, overlap_end3) is True

    # Test contained within (new reservation is inside existing)
    overlap_start4 = start1 + timedelta(minutes=30)
    overlap_end4 = end1 - timedelta(minutes=30)
    assert database.check_time_conflict(1, overlap_start4, overlap_end4) is True

    # Test no overlap (before existing reservation)
    no_overlap_start = start1 - timedelta(hours=3)
    no_overlap_end = start1 - timedelta(hours=1)
    assert database.check_time_conflict(1, no_overlap_start, no_overlap_end) is False

    # Test no overlap (after existing reservation)
    no_overlap_start2 = end1 + timedelta(hours=1)
    no_overlap_end2 = end1 + timedelta(hours=3)
    assert database.check_time_conflict(1, no_overlap_start2, no_overlap_end2) is False

    # Test exact boundary (new starts when existing ends)
    boundary_start = end1
    boundary_end = end1 + timedelta(hours=2)
    assert database.check_time_conflict(1, boundary_start, boundary_end) is False

    # Test different room (no conflict)
    assert database.check_time_conflict(2, start1, end1) is False
