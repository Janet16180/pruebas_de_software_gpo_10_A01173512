"""Hotel entity and manager."""

import logging
from dataclasses import dataclass, field
from typing import ClassVar, Optional

from persistence import EntityManager

logger = logging.getLogger(__name__)


@dataclass
class Hotel:
    """Hotel data.

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

    hotel_id: int
    name: str
    location: str
    total_rooms: int
    reserved_rooms: list[int] = field(
        default_factory=list,
        init=False,
    )


class HotelManager(EntityManager):
    """Manager for Hotel persistence and operations."""

    _prefix: ClassVar[str] = "hotel"
    _id_attr: ClassVar[str] = "hotel_id"
    _entity_cls: ClassVar[type] = Hotel

    def create(
        self,
        hotel_id: int,
        name: str,
        location: str,
        total_rooms: int,
    ) -> Optional[Hotel]:
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

        Returns
        -------
        Hotel or None
            The created hotel, or None if failed.

        Raises
        ------
        ValueError
            If hotel_id/total_rooms are not positive
            or name/location are empty.
        """
        if hotel_id <= 0:
            raise ValueError(
                f"hotel_id must be positive, got {hotel_id}",
            )
        if not name:
            raise ValueError("name must not be empty")
        if not location:
            raise ValueError("location must not be empty")
        if total_rooms <= 0:
            raise ValueError(
                f"total_rooms must be positive, got {total_rooms}",
            )
        hotel = Hotel(hotel_id, name, location, total_rooms)
        if self.save(hotel):
            return hotel
        return None

    def display_info(self, hotel: Hotel) -> str:
        """Return a human-readable summary of the hotel.

        Parameters
        ----------
        hotel : Hotel
            Hotel instance to display.

        Returns
        -------
        str
            Formatted hotel information string.
        """
        available = hotel.total_rooms - len(hotel.reserved_rooms)
        return (
            f"Hotel {hotel.name} (ID: {hotel.hotel_id})\n"
            f"  Location: {hotel.location}\n"
            f"  Rooms: {available}/{hotel.total_rooms}"
            " available"
        )

    def modify_info(
        self,
        hotel: Hotel,
        name: Optional[str] = None,
        location: Optional[str] = None,
        total_rooms: Optional[int] = None,
    ) -> bool:
        """Update hotel attributes and persist changes.

        Parameters
        ----------
        hotel : Hotel
            Hotel instance to modify.
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

        Raises
        ------
        ValueError
            If total_rooms is not positive.
        """
        if total_rooms is not None and total_rooms <= 0:
            raise ValueError(
                f"total_rooms must be positive, got {total_rooms}",
            )
        if name is not None:
            hotel.name = name
        if location is not None:
            hotel.location = location
        if total_rooms is not None:
            hotel.total_rooms = total_rooms
        return self.save(hotel)

    def reserve_room(
        self,
        hotel: Hotel,
        reservation_id: int,
    ) -> bool:
        """Reserve a room for the given reservation.

        Parameters
        ----------
        hotel : Hotel
            Hotel to reserve a room in.
        reservation_id : int
            ID of the reservation claiming the room.

        Returns
        -------
        bool
            True if reserved, False if fully booked.
        """
        if len(hotel.reserved_rooms) >= hotel.total_rooms:
            logger.error(
                "Hotel %d is fully booked.",
                hotel.hotel_id,
            )
            return False
        hotel.reserved_rooms.append(reservation_id)
        return self.save(hotel)

    def cancel_reservation(
        self,
        hotel: Hotel,
        reservation_id: int,
    ) -> bool:
        """Cancel a room reservation.

        Parameters
        ----------
        hotel : Hotel
            Hotel to cancel the reservation in.
        reservation_id : int
            ID of the reservation to cancel.

        Returns
        -------
        bool
            True if cancelled, False if not found.
        """
        if reservation_id not in hotel.reserved_rooms:
            logger.error(
                "Reservation %d not found in hotel %d.",
                reservation_id,
                hotel.hotel_id,
            )
            return False
        hotel.reserved_rooms.remove(reservation_id)
        return self.save(hotel)
