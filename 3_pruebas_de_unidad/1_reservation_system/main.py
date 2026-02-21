"""Demo script showcasing the reservation system features."""

import logging
import shutil
from pathlib import Path

from customer import CustomerManager
from hotel import HotelManager
from reservation import ReservationManager

DEMO_DIR = Path("demo_data")


def demo_crud(
    hotel_mgr: HotelManager,
    customer_mgr: CustomerManager,
    reservation_mgr: ReservationManager,
) -> None:
    """Demonstrate create, modify, and cancel operations."""
    print("Creating hotels...")
    h1 = hotel_mgr.create(1, "Grand Palace", "Downtown", 3)
    h2 = hotel_mgr.create(2, "Beach Resort", "Coastline", 2)
    print(hotel_mgr.display_info(h1))
    print(hotel_mgr.display_info(h2))
    print()

    print("Creating customers...")
    c1 = customer_mgr.create(1, "Alice Smith", "alice@mail.com")
    c2 = customer_mgr.create(2, "Bob Johnson", "bob@mail.com")
    print(customer_mgr.display_info(c1))
    print(customer_mgr.display_info(c2))
    print()

    print("Making reservations...")
    r1 = reservation_mgr.create(100, 1, 1)
    print(
        f"  Reservation {r1.reservation_id}: "
        f"customer {r1.customer_id} at hotel {r1.hotel_id}"
    )
    r2 = reservation_mgr.create(101, 2, 1)
    print(
        f"  Reservation {r2.reservation_id}: "
        f"customer {r2.customer_id} at hotel {r2.hotel_id}"
    )
    print()

    print("Hotel status after reservations:")
    h1 = hotel_mgr.load(1)
    print(hotel_mgr.display_info(h1))
    print()

    print("Modifying entities...")
    hotel_mgr.modify_info(h2, name="Sunset Beach Resort")
    print(f"  Hotel 2 renamed to: {h2.name}")
    customer_mgr.modify_info(c1, email="alice.smith@mail.com")
    print(f"  Customer 1 email updated to: {c1.email}")
    print()

    print("Cancelling reservation 100...")
    reservation_mgr.cancel(r1)
    h1 = hotel_mgr.load(1)
    print(hotel_mgr.display_info(h1))
    print()


def demo_errors(
    hotel_mgr: HotelManager,
    customer_mgr: CustomerManager,
    reservation_mgr: ReservationManager,
) -> None:
    """Demonstrate validation errors and edge cases."""
    print("Validation errors:")
    try:
        hotel_mgr.create(-1, "Bad Hotel", "Nowhere", 10)
    except ValueError as exc:
        print(f"  {exc}")

    try:
        customer_mgr.create(3, "", "no-name@mail.com")
    except ValueError as exc:
        print(f"  {exc}")

    try:
        reservation_mgr.create(200, 999, 1)
    except ValueError as exc:
        print(f"  {exc}")
    print()

    print("Hotel fully booked:")
    reservation_mgr.create(102, 1, 2)
    reservation_mgr.create(103, 2, 2)
    result = reservation_mgr.create(104, 1, 2)
    print(f"  Third reservation at Beach Resort: {result}")
    print()


def main() -> None:
    """Run a demonstration of all system features."""
    logging.disable(logging.CRITICAL)

    if DEMO_DIR.exists():
        shutil.rmtree(DEMO_DIR)
    DEMO_DIR.mkdir()

    hotel_mgr = HotelManager(DEMO_DIR)
    customer_mgr = CustomerManager(DEMO_DIR)
    reservation_mgr = ReservationManager(
        DEMO_DIR,
        hotel_mgr=hotel_mgr,
        customer_mgr=customer_mgr,
    )

    demo_crud(hotel_mgr, customer_mgr, reservation_mgr)
    demo_errors(hotel_mgr, customer_mgr, reservation_mgr)
    print(f"JSON files saved in: {DEMO_DIR.resolve()}")


if __name__ == "__main__":
    main()
