"""Reservation entity and manager."""

from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar, Optional

from customer import CustomerManager
from hotel import HotelManager
from persistence import EntityManager


@dataclass
class Reservation:
    """Reservation data.

    Parameters
    ----------
    reservation_id : int
        Unique identifier for the reservation.
    customer_id : int
        ID of the customer making the reservation.
    hotel_id : int
        ID of the hotel being reserved.
    """

    reservation_id: int
    customer_id: int
    hotel_id: int


class ReservationManager(EntityManager):
    """Manager for Reservation persistence and operations."""

    _prefix: ClassVar[str] = "reservation"
    _id_attr: ClassVar[str] = "reservation_id"
    _entity_cls: ClassVar[type] = Reservation

    def __init__(
        self,
        storage_dir: Optional[Path] = None,
        hotel_mgr: Optional[HotelManager] = None,
        customer_mgr: Optional[CustomerManager] = None,
    ) -> None:
        super().__init__(storage_dir)
        self._hotel_mgr = hotel_mgr or HotelManager(self._storage_dir)
        self._customer_mgr = customer_mgr or CustomerManager(self._storage_dir)

    def create(
        self,
        reservation_id: int,
        customer_id: int,
        hotel_id: int,
    ) -> Optional[Reservation]:
        """Create a reservation after validation.

        Loads the hotel and customer, reserves a room in the
        hotel, then persists the reservation. If the
        reservation save fails, the room is rolled back.

        Parameters
        ----------
        reservation_id : int
            Unique identifier for the reservation.
        customer_id : int
            ID of the customer making the reservation.
        hotel_id : int
            ID of the hotel being reserved.

        Returns
        -------
        Reservation or None
            The created reservation, or None if failed.

        Raises
        ------
        ValueError
            If hotel or customer does not exist.
        """
        hotel = self._hotel_mgr.load(hotel_id)
        if hotel is None:
            raise ValueError(
                f"Hotel {hotel_id} not found",
            )

        customer = self._customer_mgr.load(customer_id)
        if customer is None:
            raise ValueError(
                f"Customer {customer_id} not found",
            )

        if not self._hotel_mgr.reserve_room(
            hotel,
            reservation_id,
        ):
            return None

        reservation = Reservation(
            reservation_id,
            customer_id,
            hotel_id,
        )
        if not self.save(reservation):
            self._hotel_mgr.cancel_reservation(
                hotel,
                reservation_id,
            )
            return None
        return reservation

    def cancel(self, reservation: Reservation) -> bool:
        """Cancel a reservation.

        Removes the reservation from the hotel's reserved
        rooms and deletes the reservation file.

        Parameters
        ----------
        reservation : Reservation
            Reservation instance to cancel.

        Returns
        -------
        bool
            True if cancelled successfully.
        """
        hotel = self._hotel_mgr.load(
            reservation.hotel_id,
        )
        if hotel is not None:
            self._hotel_mgr.cancel_reservation(
                hotel,
                reservation.reservation_id,
            )
        return self.delete(reservation)
