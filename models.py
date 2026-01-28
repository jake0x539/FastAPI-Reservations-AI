from datetime import datetime
from pydantic import BaseModel, EmailStr, field_validator


class Customer(BaseModel):
    id: int
    name: str
    email: EmailStr


class Room(BaseModel):
    id: int
    name: str


class Reservation(BaseModel):
    id: int
    customer_id: int
    room_id: int
    start_time: datetime
    end_time: datetime

    @field_validator('start_time', 'end_time')
    @classmethod
    def ensure_utc(cls, v: datetime) -> datetime:
        """Ensure datetime is timezone-aware and in UTC."""
        if v.tzinfo is None:
            raise ValueError("Datetime must be timezone-aware (UTC)")
        return v

    @field_validator('end_time')
    @classmethod
    def validate_time_order(cls, v: datetime, info) -> datetime:
        """Ensure end_time is after start_time."""
        if 'start_time' in info.data and v <= info.data['start_time']:
            raise ValueError("end_time must be after start_time")
        return v


class ReservationCreate(BaseModel):
    customer_id: int
    room_id: int
    start_time: datetime
    end_time: datetime

    @field_validator('start_time', 'end_time')
    @classmethod
    def ensure_utc(cls, v: datetime) -> datetime:
        """Ensure datetime is timezone-aware and in UTC."""
        if v.tzinfo is None:
            raise ValueError("Datetime must be timezone-aware (UTC)")
        return v

    @field_validator('end_time')
    @classmethod
    def validate_time_order(cls, v: datetime, info) -> datetime:
        """Ensure end_time is after start_time."""
        if 'start_time' in info.data and v <= info.data['start_time']:
            raise ValueError("end_time must be after start_time")
        return v


class CustomerCreate(BaseModel):
    name: str
    email: EmailStr
