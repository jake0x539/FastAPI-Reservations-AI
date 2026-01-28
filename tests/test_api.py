import pytest
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient
from main import app
from src import database


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


client = TestClient(app)


def test_list_rooms():
    """Test listing all rooms."""
    response = client.get("/rooms")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 5
    assert data[0]["id"] == 1
    assert data[0]["name"] == "Conference Room A"


def test_create_customer():
    """Test creating a customer."""
    response = client.post(
        "/customers",
        json={"name": "John Doe", "email": "john@example.com"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["name"] == "John Doe"
    assert data["email"] == "john@example.com"


def test_create_customer_duplicate_email():
    """Test creating a customer with duplicate email fails."""
    client.post(
        "/customers",
        json={"name": "John Doe", "email": "john@example.com"}
    )

    response = client.post(
        "/customers",
        json={"name": "Jane Smith", "email": "john@example.com"}
    )
    assert response.status_code == 409
    assert "email 'john@example.com' already exists" in response.json()["detail"]


def test_create_customer_duplicate_name():
    """Test creating a customer with duplicate name fails."""
    client.post(
        "/customers",
        json={"name": "John Doe", "email": "john@example.com"}
    )

    response = client.post(
        "/customers",
        json={"name": "John Doe", "email": "jane@example.com"}
    )
    assert response.status_code == 409
    assert "name 'John Doe' already exists" in response.json()["detail"]


def test_create_customer_invalid_email():
    """Test creating a customer with invalid email fails."""
    response = client.post(
        "/customers",
        json={"name": "John Doe", "email": "invalid-email"}
    )
    assert response.status_code == 422


def test_create_reservation():
    """Test creating a reservation."""
    # Create a customer first
    client.post(
        "/customers",
        json={"name": "John Doe", "email": "john@example.com"}
    )

    start = datetime.now(timezone.utc) + timedelta(hours=1)
    end = start + timedelta(hours=2)

    response = client.post(
        "/reservations",
        json={
            "customer_id": 1,
            "room_id": 1,
            "start_time": start.isoformat(),
            "end_time": end.isoformat()
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["customer_id"] == 1
    assert data["room_id"] == 1


def test_create_reservation_customer_not_found():
    """Test creating a reservation with non-existent customer fails."""
    start = datetime.now(timezone.utc) + timedelta(hours=1)
    end = start + timedelta(hours=2)

    response = client.post(
        "/reservations",
        json={
            "customer_id": 999,
            "room_id": 1,
            "start_time": start.isoformat(),
            "end_time": end.isoformat()
        }
    )
    assert response.status_code == 404
    assert "Customer with id 999 not found" in response.json()["detail"]


def test_create_reservation_room_not_found():
    """Test creating a reservation with non-existent room fails."""
    client.post(
        "/customers",
        json={"name": "John Doe", "email": "john@example.com"}
    )

    start = datetime.now(timezone.utc) + timedelta(hours=1)
    end = start + timedelta(hours=2)

    response = client.post(
        "/reservations",
        json={
            "customer_id": 1,
            "room_id": 999,
            "start_time": start.isoformat(),
            "end_time": end.isoformat()
        }
    )
    assert response.status_code == 404
    assert "Room with id 999 not found" in response.json()["detail"]


def test_create_reservation_past_time():
    """Test creating a reservation in the past fails."""
    client.post(
        "/customers",
        json={"name": "John Doe", "email": "john@example.com"}
    )

    start = datetime.now(timezone.utc) - timedelta(hours=2)
    end = start + timedelta(hours=2)

    response = client.post(
        "/reservations",
        json={
            "customer_id": 1,
            "room_id": 1,
            "start_time": start.isoformat(),
            "end_time": end.isoformat()
        }
    )
    assert response.status_code == 400
    assert "Cannot create reservations in the past" in response.json()["detail"]


def test_create_reservation_end_before_start():
    """Test creating a reservation with end time before start time fails."""
    client.post(
        "/customers",
        json={"name": "John Doe", "email": "john@example.com"}
    )

    start = datetime.now(timezone.utc) + timedelta(hours=2)
    end = start - timedelta(hours=1)

    response = client.post(
        "/reservations",
        json={
            "customer_id": 1,
            "room_id": 1,
            "start_time": start.isoformat(),
            "end_time": end.isoformat()
        }
    )
    assert response.status_code == 422
    assert "end_time must be after start_time" in str(response.json())


def test_create_reservation_time_conflict():
    """Test creating a reservation with time conflict fails."""
    client.post(
        "/customers",
        json={"name": "John Doe", "email": "john@example.com"}
    )

    start1 = datetime.now(timezone.utc) + timedelta(hours=1)
    end1 = start1 + timedelta(hours=2)

    # Create first reservation
    client.post(
        "/reservations",
        json={
            "customer_id": 1,
            "room_id": 1,
            "start_time": start1.isoformat(),
            "end_time": end1.isoformat()
        }
    )

    # Try to create overlapping reservation
    start2 = start1 + timedelta(minutes=30)
    end2 = end1 + timedelta(minutes=30)

    response = client.post(
        "/reservations",
        json={
            "customer_id": 1,
            "room_id": 1,
            "start_time": start2.isoformat(),
            "end_time": end2.isoformat()
        }
    )
    assert response.status_code == 409
    assert "Time conflict" in response.json()["detail"]


def test_create_reservation_no_conflict_different_room():
    """Test creating reservations in different rooms doesn't conflict."""
    client.post(
        "/customers",
        json={"name": "John Doe", "email": "john@example.com"}
    )

    start = datetime.now(timezone.utc) + timedelta(hours=1)
    end = start + timedelta(hours=2)

    # Create reservation in room 1
    response1 = client.post(
        "/reservations",
        json={
            "customer_id": 1,
            "room_id": 1,
            "start_time": start.isoformat(),
            "end_time": end.isoformat()
        }
    )
    assert response1.status_code == 201

    # Create reservation in room 2 at the same time (should succeed)
    response2 = client.post(
        "/reservations",
        json={
            "customer_id": 1,
            "room_id": 2,
            "start_time": start.isoformat(),
            "end_time": end.isoformat()
        }
    )
    assert response2.status_code == 201


def test_create_reservation_no_conflict_different_time():
    """Test creating reservations at different times doesn't conflict."""
    client.post(
        "/customers",
        json={"name": "John Doe", "email": "john@example.com"}
    )

    start1 = datetime.now(timezone.utc) + timedelta(hours=1)
    end1 = start1 + timedelta(hours=2)

    # Create first reservation
    response1 = client.post(
        "/reservations",
        json={
            "customer_id": 1,
            "room_id": 1,
            "start_time": start1.isoformat(),
            "end_time": end1.isoformat()
        }
    )
    assert response1.status_code == 201

    # Create second reservation after the first ends (should succeed)
    start2 = end1 + timedelta(minutes=30)
    end2 = start2 + timedelta(hours=2)

    response2 = client.post(
        "/reservations",
        json={
            "customer_id": 1,
            "room_id": 1,
            "start_time": start2.isoformat(),
            "end_time": end2.isoformat()
        }
    )
    assert response2.status_code == 201


def test_delete_reservation():
    """Test deleting a reservation."""
    client.post(
        "/customers",
        json={"name": "John Doe", "email": "john@example.com"}
    )

    start = datetime.now(timezone.utc) + timedelta(hours=1)
    end = start + timedelta(hours=2)

    # Create reservation
    response = client.post(
        "/reservations",
        json={
            "customer_id": 1,
            "room_id": 1,
            "start_time": start.isoformat(),
            "end_time": end.isoformat()
        }
    )
    reservation_id = response.json()["id"]

    # Delete reservation
    response = client.delete(f"/reservations/{reservation_id}")
    assert response.status_code == 204


def test_delete_reservation_not_found():
    """Test deleting a non-existent reservation fails."""
    response = client.delete("/reservations/999")
    assert response.status_code == 404
    assert "Reservation with id 999 not found" in response.json()["detail"]


def test_get_room_reservations():
    """Test getting all reservations for a room."""
    client.post(
        "/customers",
        json={"name": "John Doe", "email": "john@example.com"}
    )

    start1 = datetime.now(timezone.utc) + timedelta(hours=1)
    end1 = start1 + timedelta(hours=2)
    start2 = datetime.now(timezone.utc) + timedelta(hours=4)
    end2 = start2 + timedelta(hours=2)

    # Create two reservations for room 1
    client.post(
        "/reservations",
        json={
            "customer_id": 1,
            "room_id": 1,
            "start_time": start1.isoformat(),
            "end_time": end1.isoformat()
        }
    )
    client.post(
        "/reservations",
        json={
            "customer_id": 1,
            "room_id": 1,
            "start_time": start2.isoformat(),
            "end_time": end2.isoformat()
        }
    )

    # Create one reservation for room 2
    client.post(
        "/reservations",
        json={
            "customer_id": 1,
            "room_id": 2,
            "start_time": start1.isoformat(),
            "end_time": end1.isoformat()
        }
    )

    # Get reservations for room 1
    response = client.get("/rooms/1/reservations")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert all(res["room_id"] == 1 for res in data)


def test_get_room_reservations_room_not_found():
    """Test getting reservations for non-existent room fails."""
    response = client.get("/rooms/999/reservations")
    assert response.status_code == 404
    assert "Room with id 999 not found" in response.json()["detail"]


def test_get_room_reservations_empty():
    """Test getting reservations for a room with no reservations."""
    response = client.get("/rooms/1/reservations")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0
