"""Unit tests for the Hotel class."""

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
from hotel import Hotel  # noqa: E402


class TestHotelCreate(unittest.TestCase):
    """Tests for Hotel.create class method."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_create_returns_hotel(self):
        hotel = Hotel.create(
            1,
            "Grand",
            "Downtown",
            10,
            storage_dir=self.tmp,
        )
        self.assertIsNotNone(hotel)
        self.assertEqual(hotel.name, "Grand")

    def test_create_persists_file(self):
        Hotel.create(
            1,
            "Grand",
            "Downtown",
            10,
            storage_dir=self.tmp,
        )
        filepath = self.tmp / "hotel_1.json"
        self.assertTrue(filepath.exists())

    def test_create_save_failure_returns_none(self):
        bad_dir = self.tmp / "nonexistent" / "deep"
        hotel = Hotel.create(
            1,
            "Grand",
            "Downtown",
            10,
            storage_dir=bad_dir,
        )
        self.assertIsNone(hotel)


class TestHotelDelete(unittest.TestCase):
    """Tests for Hotel.delete method."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_delete_removes_file(self):
        hotel = Hotel.create(
            1,
            "Grand",
            "Downtown",
            10,
            storage_dir=self.tmp,
        )
        result = hotel.delete()
        self.assertTrue(result)
        self.assertFalse((self.tmp / "hotel_1.json").exists())

    def test_delete_nonexistent_file_returns_false(self):
        hotel = Hotel(1, "Grand", "Downtown", 10)
        hotel._storage_dir = self.tmp
        result = hotel.delete()
        self.assertFalse(result)


class TestHotelDisplayInfo(unittest.TestCase):
    """Tests for Hotel.display_info method."""

    def test_display_info_format(self):
        hotel = Hotel(1, "Grand", "Downtown", 10)
        info = hotel.display_info()
        self.assertIn("Grand", info)
        self.assertIn("Downtown", info)
        self.assertIn("10/10 available", info)

    def test_display_info_with_reservations(self):
        hotel = Hotel(1, "Grand", "Downtown", 10)
        hotel.reserved_rooms = [100, 101]
        info = hotel.display_info()
        self.assertIn("8/10 available", info)


class TestHotelModifyInfo(unittest.TestCase):
    """Tests for Hotel.modify_info method."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_modify_name(self):
        hotel = Hotel.create(
            1,
            "Grand",
            "Downtown",
            10,
            storage_dir=self.tmp,
        )
        result = hotel.modify_info(name="Luxury Grand")
        self.assertTrue(result)
        self.assertEqual(hotel.name, "Luxury Grand")

    def test_modify_location(self):
        hotel = Hotel.create(
            1,
            "Grand",
            "Downtown",
            10,
            storage_dir=self.tmp,
        )
        hotel.modify_info(location="Uptown")
        self.assertEqual(hotel.location, "Uptown")

    def test_modify_total_rooms(self):
        hotel = Hotel.create(
            1,
            "Grand",
            "Downtown",
            10,
            storage_dir=self.tmp,
        )
        hotel.modify_info(total_rooms=20)
        self.assertEqual(hotel.total_rooms, 20)

    def test_modify_persists_changes(self):
        hotel = Hotel.create(
            1,
            "Grand",
            "Downtown",
            10,
            storage_dir=self.tmp,
        )
        hotel.modify_info(name="New Name")
        loaded = Hotel.load(1, storage_dir=self.tmp)
        self.assertEqual(loaded.name, "New Name")


class TestHotelReserveRoom(unittest.TestCase):
    """Tests for Hotel.reserve_room method."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_reserve_room_success(self):
        hotel = Hotel.create(
            1,
            "Grand",
            "Downtown",
            2,
            storage_dir=self.tmp,
        )
        result = hotel.reserve_room(100)
        self.assertTrue(result)
        self.assertIn(100, hotel.reserved_rooms)

    def test_reserve_room_fully_booked(self):
        hotel = Hotel.create(
            1,
            "Grand",
            "Downtown",
            1,
            storage_dir=self.tmp,
        )
        hotel.reserve_room(100)
        result = hotel.reserve_room(101)
        self.assertFalse(result)

    def test_reserve_room_persists(self):
        hotel = Hotel.create(
            1,
            "Grand",
            "Downtown",
            5,
            storage_dir=self.tmp,
        )
        hotel.reserve_room(100)
        loaded = Hotel.load(1, storage_dir=self.tmp)
        self.assertIn(100, loaded.reserved_rooms)


class TestHotelCancelReservation(unittest.TestCase):
    """Tests for Hotel.cancel_reservation method."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_cancel_existing_reservation(self):
        hotel = Hotel.create(
            1,
            "Grand",
            "Downtown",
            5,
            storage_dir=self.tmp,
        )
        hotel.reserve_room(100)
        result = hotel.cancel_reservation(100)
        self.assertTrue(result)
        self.assertNotIn(100, hotel.reserved_rooms)

    def test_cancel_nonexistent_reservation(self):
        hotel = Hotel.create(
            1,
            "Grand",
            "Downtown",
            5,
            storage_dir=self.tmp,
        )
        result = hotel.cancel_reservation(999)
        self.assertFalse(result)


class TestHotelPersistence(unittest.TestCase):
    """Tests for Hotel save/load/to_dict/from_dict."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_save_and_load_roundtrip(self):
        hotel = Hotel(1, "Grand", "Downtown", 10)
        hotel._storage_dir = self.tmp
        hotel.reserved_rooms = [100]
        hotel.save()
        loaded = Hotel.load(1, storage_dir=self.tmp)
        self.assertEqual(loaded.hotel_id, 1)
        self.assertEqual(loaded.name, "Grand")
        self.assertEqual(loaded.reserved_rooms, [100])

    def test_load_nonexistent_returns_none(self):
        result = Hotel.load(999, storage_dir=self.tmp)
        self.assertIsNone(result)

    def test_load_corrupt_json_returns_none(self):
        filepath = self.tmp / "hotel_1.json"
        filepath.write_text("not valid json")
        result = Hotel.load(1, storage_dir=self.tmp)
        self.assertIsNone(result)

    def test_to_dict_contains_all_fields(self):
        hotel = Hotel(1, "Grand", "Downtown", 10)
        d = hotel.to_dict()
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
        hotel = Hotel.from_dict(data, storage_dir=self.tmp)
        self.assertEqual(hotel.hotel_id, 1)
        self.assertEqual(hotel.reserved_rooms, [100])

    def test_load_missing_key_returns_none(self):
        filepath = self.tmp / "hotel_1.json"
        filepath.write_text(json.dumps({"hotel_id": 1}))
        result = Hotel.load(1, storage_dir=self.tmp)
        self.assertIsNone(result)

    def test_default_storage_dir(self):
        hotel = Hotel(1, "Grand", "Downtown", 10)
        self.assertEqual(hotel._storage_dir, Path("."))


if __name__ == "__main__":
    unittest.main()
