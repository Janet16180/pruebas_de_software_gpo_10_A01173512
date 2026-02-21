"""Unit tests for Reservation and ReservationManager."""

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
from hotel import HotelManager  # noqa: E402
from customer import CustomerManager  # noqa: E402
from reservation import (  # noqa: E402
    Reservation,
    ReservationManager,
)


class TestReservationCreate(unittest.TestCase):
    """Tests for ReservationManager.create."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.hotel_mgr = HotelManager(self.tmp)
        self.customer_mgr = CustomerManager(self.tmp)
        self.mgr = ReservationManager(
            self.tmp,
            hotel_mgr=self.hotel_mgr,
            customer_mgr=self.customer_mgr,
        )
        self.hotel_mgr.create(
            1,
            "Grand",
            "Downtown",
            5,
        )
        self.customer_mgr.create(
            1,
            "Alice",
            "alice@test.com",
        )

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_create_returns_reservation(self):
        res = self.mgr.create(100, 1, 1)
        self.assertIsNotNone(res)
        self.assertEqual(res.reservation_id, 100)

    def test_create_persists_file(self):
        self.mgr.create(100, 1, 1)
        filepath = self.tmp / "reservation_100.json"
        self.assertTrue(filepath.exists())

    def test_create_reserves_room_in_hotel(self):
        self.mgr.create(100, 1, 1)
        hotel = self.hotel_mgr.load(1)
        self.assertIn(100, hotel.reserved_rooms)

    def test_create_hotel_not_found_raises(self):
        with self.assertRaises(ValueError):
            self.mgr.create(100, 1, 999)

    def test_create_customer_not_found_raises(self):
        with self.assertRaises(ValueError):
            self.mgr.create(100, 999, 1)

    def test_create_hotel_fully_booked_returns_none(self):
        self.hotel_mgr.create(2, "Tiny", "Suburbs", 1)
        self.mgr.create(100, 1, 2)
        res = self.mgr.create(101, 1, 2)
        self.assertIsNone(res)

    def test_create_rollback_on_save_failure(self):
        with patch.object(
            self.mgr,
            "save",
            return_value=False,
        ):
            res = self.mgr.create(100, 1, 1)
        self.assertIsNone(res)
        hotel = self.hotel_mgr.load(1)
        self.assertNotIn(100, hotel.reserved_rooms)


class TestReservationCancel(unittest.TestCase):
    """Tests for ReservationManager.cancel."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.hotel_mgr = HotelManager(self.tmp)
        self.customer_mgr = CustomerManager(self.tmp)
        self.mgr = ReservationManager(
            self.tmp,
            hotel_mgr=self.hotel_mgr,
            customer_mgr=self.customer_mgr,
        )
        self.hotel_mgr.create(
            1,
            "Grand",
            "Downtown",
            5,
        )
        self.customer_mgr.create(
            1,
            "Alice",
            "alice@test.com",
        )

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_cancel_removes_file(self):
        res = self.mgr.create(100, 1, 1)
        result = self.mgr.cancel(res)
        self.assertTrue(result)
        filepath = self.tmp / "reservation_100.json"
        self.assertFalse(filepath.exists())

    def test_cancel_frees_hotel_room(self):
        res = self.mgr.create(100, 1, 1)
        self.mgr.cancel(res)
        hotel = self.hotel_mgr.load(1)
        self.assertNotIn(100, hotel.reserved_rooms)

    def test_cancel_with_missing_hotel(self):
        res = self.mgr.create(100, 1, 1)
        (self.tmp / "hotel_1.json").unlink()
        result = self.mgr.cancel(res)
        self.assertTrue(result)

    def test_cancel_nonexistent_file_returns_false(self):
        res = Reservation(100, 1, 1)
        result = self.mgr.cancel(res)
        self.assertFalse(result)


class TestReservationPersistence(unittest.TestCase):
    """Tests for Reservation save/load/to_dict/from_dict."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.mgr = ReservationManager(self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_save_and_load_roundtrip(self):
        res = Reservation(100, 1, 1)
        self.mgr.save(res)
        loaded = self.mgr.load(100)
        self.assertEqual(loaded.reservation_id, 100)
        self.assertEqual(loaded.customer_id, 1)
        self.assertEqual(loaded.hotel_id, 1)

    def test_load_nonexistent_returns_none(self):
        result = self.mgr.load(999)
        self.assertIsNone(result)

    def test_load_corrupt_json_returns_none(self):
        filepath = self.tmp / "reservation_100.json"
        filepath.write_text("not valid json")
        result = self.mgr.load(100)
        self.assertIsNone(result)

    def test_to_dict_contains_all_fields(self):
        res = Reservation(100, 1, 1)
        d = self.mgr.to_dict(res)
        self.assertEqual(d["reservation_id"], 100)
        self.assertEqual(d["customer_id"], 1)
        self.assertEqual(d["hotel_id"], 1)

    def test_from_dict_reconstructs_reservation(self):
        data = {
            "reservation_id": 100,
            "customer_id": 1,
            "hotel_id": 1,
        }
        res = self.mgr.from_dict(data)
        self.assertEqual(res.reservation_id, 100)

    def test_save_failure_returns_false(self):
        bad_dir = self.tmp / "nonexistent" / "deep"
        mgr = ReservationManager(bad_dir)
        res = Reservation(100, 1, 1)
        result = mgr.save(res)
        self.assertFalse(result)

    def test_load_missing_key_returns_none(self):
        filepath = self.tmp / "reservation_100.json"
        filepath.write_text(
            json.dumps({"reservation_id": 100}),
        )
        result = self.mgr.load(100)
        self.assertIsNone(result)

    def test_default_storage_dir(self):
        mgr = ReservationManager()
        self.assertEqual(mgr._storage_dir, Path("."))


class TestReservationIntegration(unittest.TestCase):
    """Integration tests for reservation workflow."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.hotel_mgr = HotelManager(self.tmp)
        self.customer_mgr = CustomerManager(self.tmp)
        self.mgr = ReservationManager(
            self.tmp,
            hotel_mgr=self.hotel_mgr,
            customer_mgr=self.customer_mgr,
        )
        self.hotel_mgr.create(
            1,
            "Grand",
            "Downtown",
            3,
        )
        self.customer_mgr.create(
            1,
            "Alice",
            "alice@test.com",
        )
        self.customer_mgr.create(
            2,
            "Bob",
            "bob@test.com",
        )

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_multiple_reservations(self):
        r1 = self.mgr.create(100, 1, 1)
        r2 = self.mgr.create(101, 2, 1)
        self.assertIsNotNone(r1)
        self.assertIsNotNone(r2)
        hotel = self.hotel_mgr.load(1)
        self.assertEqual(len(hotel.reserved_rooms), 2)

    def test_cancel_frees_room_for_new_reservation(self):
        self.hotel_mgr.create(2, "Tiny", "Suburbs", 1)
        r1 = self.mgr.create(100, 1, 2)
        self.mgr.cancel(r1)
        r2 = self.mgr.create(101, 2, 2)
        self.assertIsNotNone(r2)

    def test_full_lifecycle(self):
        res = self.mgr.create(100, 1, 1)
        loaded = self.mgr.load(100)
        self.assertEqual(
            loaded.reservation_id,
            res.reservation_id,
        )
        self.mgr.cancel(loaded)
        self.assertIsNone(self.mgr.load(100))


if __name__ == "__main__":
    unittest.main()
