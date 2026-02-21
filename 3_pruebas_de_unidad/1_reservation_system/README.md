Reservation System
==================

A hotel reservation system with JSON file persistence, built as a unit testing exercise.

The system manages three entities (Hotel, Customer, Reservation) using pure dataclasses
for data and dedicated Manager classes for persistence and business logic.


Project Structure
-----------------

::

    hotel.py          Hotel dataclass + HotelManager
    customer.py       Customer dataclass + CustomerManager
    reservation.py    Reservation dataclass + ReservationManager
    persistence.py    EntityManager base class (shared JSON persistence)
    tests/
        test_hotel.py
        test_customer.py
        test_reservation.py


Design Decisions
----------------

1. Data vs behavior separation: Entities are plain dataclasses that only hold data.
   All persistence, validation, and business logic lives in Manager classes.

2. EntityManager base class: Shared save/load/delete/to_dict/from_dict logic
   is defined once in persistence.py. Each Manager subclass only needs to set
   three class variables (_prefix, _id_attr, _entity_cls) to get full JSON
   persistence for free.

3. Validation at boundaries: Manager.create() and modify_info() raise ValueError
   for invalid input (negative IDs, empty strings, non-positive room counts).
   Operational failures (I/O errors, missing files) return None or False.

4. Dependency injection: ReservationManager receives HotelManager and
   CustomerManager as optional constructor arguments, making it easy to
   test in isolation with temporary directories.


Running Tests
-------------

::

    python -m unittest discover -s tests -v

Coverage report::

    python -m coverage run -m unittest discover -s tests
    python -m coverage report

Linting::

    pylint persistence.py hotel.py customer.py reservation.py
    ruff check .
    flake8 .
