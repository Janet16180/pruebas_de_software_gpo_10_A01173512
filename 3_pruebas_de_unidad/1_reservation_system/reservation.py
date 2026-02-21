"""Reservation entity with JSON file persistence."""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar, Optional

from customer import Customer
from hotel import Hotel
from persistence import PersistentEntity

logger = logging.getLogger(__name__)


@dataclass
class Reservation(PersistentEntity):
    """Represent a hotel room reservation.

    Parameters
    ----------
    reservation_id : int
        Unique identifier for the reservation.
    customer_id : int
        ID of the customer making the reservation.
    hotel_id : int
        ID of the hotel being reserved.
    """

    _prefix: ClassVar[str] = "reservation"
    _id_attr: ClassVar[str] = "reservation_id"

    reservation_id: int
    customer_id: int
    hotel_id: int

    @classmethod
    def create(
        cls,
        reservation_id: int,
        customer_id: int,
        hotel_id: int,
        *,
        storage_dir: Optional[Path] = None,
    ) -> Optional["Reservation"]:
        """Create a reservation after validation.

        Loads the hotel and customer from disk, reserves
        a room in the hotel, then persists the reservation.
        If the reservation file save fails, the room
        reservation is rolled back.

        Parameters
        ----------
        reservation_id : int
            Unique identifier for the reservation.
        customer_id : int
            ID of the customer making the reservation.
        hotel_id : int
            ID of the hotel being reserved.
        storage_dir : Path, optional
            Directory for JSON file persistence.

        Returns
        -------
        Reservation or None
            The created reservation, or None if failed.
        """
        sdir = storage_dir or Path(".")
        hotel = Hotel.load(hotel_id, storage_dir=sdir)
        if hotel is None:
            logger.error(
                "Hotel %d not found.",
                hotel_id,
            )
            return None

        customer = Customer.load(
            customer_id,
            storage_dir=sdir,
        )
        if customer is None:
            logger.error(
                "Customer %d not found.",
                customer_id,
            )
            return None

        if not hotel.reserve_room(reservation_id):
            return None

        reservation = cls(
            reservation_id,
            customer_id,
            hotel_id,
        )
        reservation._storage_dir = sdir
        if not reservation.save():
            hotel.cancel_reservation(reservation_id)
            return None
        return reservation

    def cancel(self) -> bool:
        """Cancel this reservation.

        Removes the reservation from the hotel's reserved
        rooms and deletes the reservation file.

        Returns
        -------
        bool
            True if cancelled successfully.
        """
        hotel = Hotel.load(
            self.hotel_id,
            storage_dir=self._storage_dir,
        )
        if hotel is not None:
            hotel.cancel_reservation(
                self.reservation_id,
            )
        return self.delete()
