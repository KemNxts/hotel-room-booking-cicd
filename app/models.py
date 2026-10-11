"""Model layer: plain data objects passed between the layers.

They hold data only - no SQL and no business rules - so every layer can use
them without depending on the database or on Flask.
"""
from dataclasses import dataclass
from datetime import date


class BookingStatus:
    PENDING = "PENDING"      # requested; room is held, waiting for the guest to confirm
    CONFIRMED = "CONFIRMED"  # guest confirmed the booking
    CANCELLED = "CANCELLED"  # cancelled by the guest; room is free again

    # Statuses that occupy a room. A cancelled booking does not.
    ACTIVE = (PENDING, CONFIRMED)


@dataclass
class User:
    id: int
    email: str
    full_name: str
    password_hash: str

    @classmethod
    def from_row(cls, row):
        return cls(row["id"], row["email"], row["full_name"], row["password_hash"])


@dataclass
class Room:
    id: int
    room_number: str
    room_type: str
    capacity: int
    price_per_night: int

    @classmethod
    def from_row(cls, row):
        return cls(row["id"], row["room_number"], row["room_type"],
                   row["capacity"], row["price_per_night"])


@dataclass
class Booking:
    id: int
    user_id: int
    room_id: int
    check_in: date
    check_out: date
    total_price: int
    status: str
    created_at: str
    # Filled in when the DAO joins the rooms table, for display purposes.
    room_number: str = ""
    room_type: str = ""

    @property
    def nights(self):
        return (self.check_out - self.check_in).days

    @property
    def can_confirm(self):
        return self.status == BookingStatus.PENDING

    @property
    def can_cancel(self):
        return self.status in BookingStatus.ACTIVE

    @classmethod
    def from_row(cls, row):
        keys = row.keys()
        return cls(
            id=row["id"],
            user_id=row["user_id"],
            room_id=row["room_id"],
            check_in=date.fromisoformat(row["check_in"]),
            check_out=date.fromisoformat(row["check_out"]),
            total_price=row["total_price"],
            status=row["status"],
            created_at=row["created_at"],
            room_number=row["room_number"] if "room_number" in keys else "",
            room_type=row["room_type"] if "room_type" in keys else "",
        )
