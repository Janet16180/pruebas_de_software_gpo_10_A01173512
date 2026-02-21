"""Unit tests for the Reservation class."""

import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import sys

sys.path.insert(
    0,
    str(Path(__file__).resolve().parent.parent),
)
from hotel import Hotel  # noqa: E402
from customer import Customer  # noqa: E402
from reservation import Reservation  # noqa: E402


class TestReservationCreate(unittest.TestCase):
    """Tests for Reservation.create class method."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        Hotel.create(
            1,
            "Grand",
            "Downtown",
            5,
            storage_dir=self.tmp,
        )
        Customer.create(
            1,
            "Alice",
            "alice@test.com",
            storage_dir=self.tmp,
        )

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_create_returns_reservation(self):
        res = Reservation.create(
            100,
            1,
            1,
            storage_dir=self.tmp,
        )
        self.assertIsNotNone(res)
        self.assertEqual(res.reservation_id, 100)

    def test_create_persists_file(self):
        Reservation.create(
            100,
            1,
            1,
            storage_dir=self.tmp,
        )
        filepath = self.tmp / "reservation_100.json"
        self.assertTrue(filepath.exists())

    def test_create_reserves_room_in_hotel(self):
        Reservation.create(
            100,
            1,
            1,
            storage_dir=self.tmp,
        )
        hotel = Hotel.load(1, storage_dir=self.tmp)
        self.assertIn(100, hotel.reserved_rooms)

    def test_create_hotel_not_found_returns_none(self):
        res = Reservation.create(
            100,
            1,
            999,
            storage_dir=self.tmp,
        )
        self.assertIsNone(res)

    def test_create_customer_not_found_returns_none(self):
        res = Reservation.create(
            100,
            999,
            1,
            storage_dir=self.tmp,
        )
        self.assertIsNone(res)

    def test_create_hotel_fully_booked_returns_none(self):
        Hotel.create(
            2,
            "Tiny",
            "Suburbs",
            1,
            storage_dir=self.tmp,
        )
        Reservation.create(
            100,
            1,
            2,
            storage_dir=self.tmp,
        )
        res = Reservation.create(
            101,
            1,
            2,
            storage_dir=self.tmp,
        )
        self.assertIsNone(res)

    def test_create_rollback_on_save_failure(self):
        with patch.object(
            Reservation,
            "save",
            return_value=False,
        ):
            res = Reservation.create(
                100,
                1,
                1,
                storage_dir=self.tmp,
            )
        self.assertIsNone(res)
        hotel = Hotel.load(1, storage_dir=self.tmp)
        self.assertNotIn(100, hotel.reserved_rooms)


class TestReservationCancel(unittest.TestCase):
    """Tests for Reservation.cancel method."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        Hotel.create(
            1,
            "Grand",
            "Downtown",
            5,
            storage_dir=self.tmp,
        )
        Customer.create(
            1,
            "Alice",
            "alice@test.com",
            storage_dir=self.tmp,
        )

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_cancel_removes_file(self):
        res = Reservation.create(
            100,
            1,
            1,
            storage_dir=self.tmp,
        )
        result = res.cancel()
        self.assertTrue(result)
        filepath = self.tmp / "reservation_100.json"
        self.assertFalse(filepath.exists())

    def test_cancel_frees_hotel_room(self):
        res = Reservation.create(
            100,
            1,
            1,
            storage_dir=self.tmp,
        )
        res.cancel()
        hotel = Hotel.load(1, storage_dir=self.tmp)
        self.assertNotIn(100, hotel.reserved_rooms)

    def test_cancel_with_missing_hotel(self):
        res = Reservation.create(
            100,
            1,
            1,
            storage_dir=self.tmp,
        )
        (self.tmp / "hotel_1.json").unlink()
        result = res.cancel()
        self.assertTrue(result)

    def test_cancel_nonexistent_file_returns_false(self):
        res = Reservation(100, 1, 1)
        res._storage_dir = self.tmp
        result = res.cancel()
        self.assertFalse(result)


class TestReservationPersistence(unittest.TestCase):
    """Tests for Reservation save/load/to_dict/from_dict."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_save_and_load_roundtrip(self):
        res = Reservation(100, 1, 1)
        res._storage_dir = self.tmp
        res.save()
        loaded = Reservation.load(
            100,
            storage_dir=self.tmp,
        )
        self.assertEqual(loaded.reservation_id, 100)
        self.assertEqual(loaded.customer_id, 1)
        self.assertEqual(loaded.hotel_id, 1)

    def test_load_nonexistent_returns_none(self):
        result = Reservation.load(
            999,
            storage_dir=self.tmp,
        )
        self.assertIsNone(result)

    def test_load_corrupt_json_returns_none(self):
        filepath = self.tmp / "reservation_100.json"
        filepath.write_text("not valid json")
        result = Reservation.load(
            100,
            storage_dir=self.tmp,
        )
        self.assertIsNone(result)

    def test_to_dict_contains_all_fields(self):
        res = Reservation(100, 1, 1)
        d = res.to_dict()
        self.assertEqual(d["reservation_id"], 100)
        self.assertEqual(d["customer_id"], 1)
        self.assertEqual(d["hotel_id"], 1)

    def test_from_dict_reconstructs_reservation(self):
        data = {
            "reservation_id": 100,
            "customer_id": 1,
            "hotel_id": 1,
        }
        res = Reservation.from_dict(
            data,
            storage_dir=self.tmp,
        )
        self.assertEqual(res.reservation_id, 100)

    def test_save_failure_returns_false(self):
        bad_dir = self.tmp / "nonexistent" / "deep"
        res = Reservation(100, 1, 1)
        res._storage_dir = bad_dir
        result = res.save()
        self.assertFalse(result)

    def test_load_missing_key_returns_none(self):
        filepath = self.tmp / "reservation_100.json"
        filepath.write_text(json.dumps({"reservation_id": 100}))
        result = Reservation.load(
            100,
            storage_dir=self.tmp,
        )
        self.assertIsNone(result)

    def test_default_storage_dir(self):
        res = Reservation(100, 1, 1)
        self.assertEqual(res._storage_dir, Path("."))


class TestReservationIntegration(unittest.TestCase):
    """Integration tests for reservation workflow."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        Hotel.create(
            1,
            "Grand",
            "Downtown",
            3,
            storage_dir=self.tmp,
        )
        Customer.create(
            1,
            "Alice",
            "alice@test.com",
            storage_dir=self.tmp,
        )
        Customer.create(
            2,
            "Bob",
            "bob@test.com",
            storage_dir=self.tmp,
        )

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_multiple_reservations(self):
        r1 = Reservation.create(
            100,
            1,
            1,
            storage_dir=self.tmp,
        )
        r2 = Reservation.create(
            101,
            2,
            1,
            storage_dir=self.tmp,
        )
        self.assertIsNotNone(r1)
        self.assertIsNotNone(r2)
        hotel = Hotel.load(1, storage_dir=self.tmp)
        self.assertEqual(len(hotel.reserved_rooms), 2)

    def test_cancel_frees_room_for_new_reservation(self):
        Hotel.create(
            2,
            "Tiny",
            "Suburbs",
            1,
            storage_dir=self.tmp,
        )
        r1 = Reservation.create(
            100,
            1,
            2,
            storage_dir=self.tmp,
        )
        r1.cancel()
        r2 = Reservation.create(
            101,
            2,
            2,
            storage_dir=self.tmp,
        )
        self.assertIsNotNone(r2)

    def test_full_lifecycle(self):
        res = Reservation.create(
            100,
            1,
            1,
            storage_dir=self.tmp,
        )
        loaded = Reservation.load(
            100,
            storage_dir=self.tmp,
        )
        self.assertEqual(
            loaded.reservation_id,
            res.reservation_id,
        )
        loaded.cancel()
        self.assertIsNone(Reservation.load(100, storage_dir=self.tmp))


if __name__ == "__main__":
    unittest.main()
