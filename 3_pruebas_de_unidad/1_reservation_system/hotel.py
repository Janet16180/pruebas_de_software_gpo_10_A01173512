"""Hotel entity with JSON file persistence."""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import ClassVar, Optional

from persistence import PersistentEntity

logger = logging.getLogger(__name__)


@dataclass
class Hotel(PersistentEntity):
    """Represent a hotel with rooms that can be reserved.

    Parameters
    ----------
    hotel_id : int
        Unique identifier for the hotel.
    name : str
        Name of the hotel.
    location : str
        Location of the hotel.
    total_rooms : int
        Total number of rooms available.
    """

    _prefix: ClassVar[str] = "hotel"
    _id_attr: ClassVar[str] = "hotel_id"

    hotel_id: int
    name: str
    location: str
    total_rooms: int
    reserved_rooms: list[int] = field(
        default_factory=list,
        init=False,
    )

    @classmethod
    def create(  # pylint: disable=too-many-arguments
        cls,
        hotel_id: int,
        name: str,
        location: str,
        total_rooms: int,
        *,
        storage_dir: Optional[Path] = None,
    ) -> Optional["Hotel"]:
        """Create a new hotel and persist it to disk.

        Parameters
        ----------
        hotel_id : int
            Unique identifier for the hotel.
        name : str
            Name of the hotel.
        location : str
            Location of the hotel.
        total_rooms : int
            Total number of rooms available.
        storage_dir : Path, optional
            Directory for JSON file persistence.

        Returns
        -------
        Hotel or None
            The created hotel, or None if creation failed.
        """
        hotel = cls(hotel_id, name, location, total_rooms)
        hotel._storage_dir = storage_dir or Path(".")
        if hotel.save():
            return hotel
        return None

    def display_info(self) -> str:
        """Return a human-readable summary of the hotel.

        Returns
        -------
        str
            Formatted hotel information string.
        """
        available = self.total_rooms - len(self.reserved_rooms)
        return (
            f"Hotel {self.name} (ID: {self.hotel_id})\n"
            f"  Location: {self.location}\n"
            f"  Rooms: {available}/{self.total_rooms}"
            " available"
        )

    def modify_info(
        self,
        name: Optional[str] = None,
        location: Optional[str] = None,
        total_rooms: Optional[int] = None,
    ) -> bool:
        """Update hotel attributes and persist changes.

        Parameters
        ----------
        name : str, optional
            New name for the hotel.
        location : str, optional
            New location for the hotel.
        total_rooms : int, optional
            New total room count.

        Returns
        -------
        bool
            True if modifications were saved.
        """
        if name is not None:
            self.name = name
        if location is not None:
            self.location = location
        if total_rooms is not None:
            self.total_rooms = total_rooms
        return self.save()

    def reserve_room(self, reservation_id: int) -> bool:
        """Reserve a room for the given reservation.

        Parameters
        ----------
        reservation_id : int
            ID of the reservation claiming the room.

        Returns
        -------
        bool
            True if reserved, False if fully booked.
        """
        if len(self.reserved_rooms) >= self.total_rooms:
            logger.error(
                "Hotel %d is fully booked.",
                self.hotel_id,
            )
            return False
        self.reserved_rooms.append(reservation_id)
        return self.save()

    def cancel_reservation(
        self,
        reservation_id: int,
    ) -> bool:
        """Cancel a room reservation.

        Parameters
        ----------
        reservation_id : int
            ID of the reservation to cancel.

        Returns
        -------
        bool
            True if cancelled, False if not found.
        """
        if reservation_id not in self.reserved_rooms:
            logger.error(
                "Reservation %d not found in hotel %d.",
                reservation_id,
                self.hotel_id,
            )
            return False
        self.reserved_rooms.remove(reservation_id)
        return self.save()
