"""Unit tests for Hotel and HotelManager."""

import json
import shutil
import tempfile
import unittest
from pathlib import Path

import sys

sys.path.insert(
    0,
    str(Path(__file__).resolve().parent.parent),
)
from hotel import Hotel, HotelManager  # noqa: E402


class TestHotelCreate(unittest.TestCase):
    """Tests for HotelManager.create."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.mgr = HotelManager(self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_create_returns_hotel(self):
        hotel = self.mgr.create(
            1,
            "Grand",
            "Downtown",
            10,
        )
        self.assertIsNotNone(hotel)
        self.assertEqual(hotel.name, "Grand")

    def test_create_persists_file(self):
        self.mgr.create(1, "Grand", "Downtown", 10)
        filepath = self.tmp / "hotel_1.json"
        self.assertTrue(filepath.exists())

    def test_create_save_failure_returns_none(self):
        bad_dir = self.tmp / "nonexistent" / "deep"
        mgr = HotelManager(bad_dir)
        hotel = mgr.create(1, "Grand", "Downtown", 10)
        self.assertIsNone(hotel)


class TestHotelDelete(unittest.TestCase):
    """Tests for HotelManager.delete."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.mgr = HotelManager(self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_delete_removes_file(self):
        hotel = self.mgr.create(
            1,
            "Grand",
            "Downtown",
            10,
        )
        result = self.mgr.delete(hotel)
        self.assertTrue(result)
        filepath = self.tmp / "hotel_1.json"
        self.assertFalse(filepath.exists())

    def test_delete_nonexistent_file_returns_false(self):
        hotel = Hotel(1, "Grand", "Downtown", 10)
        result = self.mgr.delete(hotel)
        self.assertFalse(result)


class TestHotelDisplayInfo(unittest.TestCase):
    """Tests for HotelManager.display_info."""

    def setUp(self):
        self.mgr = HotelManager()

    def test_display_info_format(self):
        hotel = Hotel(1, "Grand", "Downtown", 10)
        info = self.mgr.display_info(hotel)
        self.assertIn("Grand", info)
        self.assertIn("Downtown", info)
        self.assertIn("10/10 available", info)

    def test_display_info_with_reservations(self):
        hotel = Hotel(1, "Grand", "Downtown", 10)
        hotel.reserved_rooms = [100, 101]
        info = self.mgr.display_info(hotel)
        self.assertIn("8/10 available", info)


class TestHotelModifyInfo(unittest.TestCase):
    """Tests for HotelManager.modify_info."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.mgr = HotelManager(self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_modify_name(self):
        hotel = self.mgr.create(
            1,
            "Grand",
            "Downtown",
            10,
        )
        result = self.mgr.modify_info(
            hotel,
            name="Luxury Grand",
        )
        self.assertTrue(result)
        self.assertEqual(hotel.name, "Luxury Grand")

    def test_modify_location(self):
        hotel = self.mgr.create(
            1,
            "Grand",
            "Downtown",
            10,
        )
        self.mgr.modify_info(hotel, location="Uptown")
        self.assertEqual(hotel.location, "Uptown")

    def test_modify_total_rooms(self):
        hotel = self.mgr.create(
            1,
            "Grand",
            "Downtown",
            10,
        )
        self.mgr.modify_info(hotel, total_rooms=20)
        self.assertEqual(hotel.total_rooms, 20)

    def test_modify_persists_changes(self):
        hotel = self.mgr.create(
            1,
            "Grand",
            "Downtown",
            10,
        )
        self.mgr.modify_info(hotel, name="New Name")
        loaded = self.mgr.load(1)
        self.assertEqual(loaded.name, "New Name")


class TestHotelReserveRoom(unittest.TestCase):
    """Tests for HotelManager.reserve_room."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.mgr = HotelManager(self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_reserve_room_success(self):
        hotel = self.mgr.create(
            1,
            "Grand",
            "Downtown",
            2,
        )
        result = self.mgr.reserve_room(hotel, 100)
        self.assertTrue(result)
        self.assertIn(100, hotel.reserved_rooms)

    def test_reserve_room_fully_booked(self):
        hotel = self.mgr.create(
            1,
            "Grand",
            "Downtown",
            1,
        )
        self.mgr.reserve_room(hotel, 100)
        result = self.mgr.reserve_room(hotel, 101)
        self.assertFalse(result)

    def test_reserve_room_persists(self):
        hotel = self.mgr.create(
            1,
            "Grand",
            "Downtown",
            5,
        )
        self.mgr.reserve_room(hotel, 100)
        loaded = self.mgr.load(1)
        self.assertIn(100, loaded.reserved_rooms)


class TestHotelCancelReservation(unittest.TestCase):
    """Tests for HotelManager.cancel_reservation."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.mgr = HotelManager(self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_cancel_existing_reservation(self):
        hotel = self.mgr.create(
            1,
            "Grand",
            "Downtown",
            5,
        )
        self.mgr.reserve_room(hotel, 100)
        result = self.mgr.cancel_reservation(hotel, 100)
        self.assertTrue(result)
        self.assertNotIn(100, hotel.reserved_rooms)

    def test_cancel_nonexistent_reservation(self):
        hotel = self.mgr.create(
            1,
            "Grand",
            "Downtown",
            5,
        )
        result = self.mgr.cancel_reservation(hotel, 999)
        self.assertFalse(result)


class TestHotelPersistence(unittest.TestCase):
    """Tests for Hotel save/load/to_dict/from_dict."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.mgr = HotelManager(self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_save_and_load_roundtrip(self):
        hotel = Hotel(1, "Grand", "Downtown", 10)
        hotel.reserved_rooms = [100]
        self.mgr.save(hotel)
        loaded = self.mgr.load(1)
        self.assertEqual(loaded.hotel_id, 1)
        self.assertEqual(loaded.name, "Grand")
        self.assertEqual(loaded.reserved_rooms, [100])

    def test_load_nonexistent_returns_none(self):
        result = self.mgr.load(999)
        self.assertIsNone(result)

    def test_load_corrupt_json_returns_none(self):
        filepath = self.tmp / "hotel_1.json"
        filepath.write_text("not valid json")
        result = self.mgr.load(1)
        self.assertIsNone(result)

    def test_to_dict_contains_all_fields(self):
        hotel = Hotel(1, "Grand", "Downtown", 10)
        d = self.mgr.to_dict(hotel)
        self.assertEqual(d["hotel_id"], 1)
        self.assertEqual(d["name"], "Grand")
        self.assertEqual(d["location"], "Downtown")
        self.assertEqual(d["total_rooms"], 10)
        self.assertIn("reserved_rooms", d)

    def test_from_dict_reconstructs_hotel(self):
        data = {
            "hotel_id": 1,
            "name": "Grand",
            "location": "Downtown",
            "total_rooms": 10,
            "reserved_rooms": [100],
        }
        hotel = self.mgr.from_dict(data)
        self.assertEqual(hotel.hotel_id, 1)
        self.assertEqual(hotel.reserved_rooms, [100])

    def test_load_missing_key_returns_none(self):
        filepath = self.tmp / "hotel_1.json"
        filepath.write_text(json.dumps({"hotel_id": 1}))
        result = self.mgr.load(1)
        self.assertIsNone(result)

    def test_default_storage_dir(self):
        mgr = HotelManager()
        self.assertEqual(mgr._storage_dir, Path("."))


if __name__ == "__main__":
    unittest.main()
