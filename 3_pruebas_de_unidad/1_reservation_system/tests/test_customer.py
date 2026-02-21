"""Unit tests for Customer and CustomerManager."""

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
from customer import Customer, CustomerManager  # noqa: E402


class TestCustomerCreate(unittest.TestCase):
    """Tests for CustomerManager.create."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.mgr = CustomerManager(self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_create_returns_customer(self):
        customer = self.mgr.create(
            1,
            "Alice",
            "alice@test.com",
        )
        self.assertIsNotNone(customer)
        self.assertEqual(customer.name, "Alice")

    def test_create_persists_file(self):
        self.mgr.create(1, "Alice", "alice@test.com")
        filepath = self.tmp / "customer_1.json"
        self.assertTrue(filepath.exists())

    def test_create_save_failure_returns_none(self):
        bad_dir = self.tmp / "nonexistent" / "deep"
        mgr = CustomerManager(bad_dir)
        customer = mgr.create(
            1,
            "Alice",
            "alice@test.com",
        )
        self.assertIsNone(customer)

    def test_create_negative_id_raises(self):
        with self.assertRaises(ValueError):
            self.mgr.create(-1, "Alice", "alice@test.com")

    def test_create_zero_id_raises(self):
        with self.assertRaises(ValueError):
            self.mgr.create(0, "Alice", "alice@test.com")

    def test_create_empty_name_raises(self):
        with self.assertRaises(ValueError):
            self.mgr.create(1, "", "alice@test.com")

    def test_create_empty_email_raises(self):
        with self.assertRaises(ValueError):
            self.mgr.create(1, "Alice", "")


class TestCustomerDelete(unittest.TestCase):
    """Tests for CustomerManager.delete."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.mgr = CustomerManager(self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_delete_removes_file(self):
        customer = self.mgr.create(
            1,
            "Alice",
            "alice@test.com",
        )
        result = self.mgr.delete(customer)
        self.assertTrue(result)
        filepath = self.tmp / "customer_1.json"
        self.assertFalse(filepath.exists())

    def test_delete_nonexistent_returns_false(self):
        customer = Customer(1, "Alice", "alice@test.com")
        result = self.mgr.delete(customer)
        self.assertFalse(result)


class TestCustomerDisplayInfo(unittest.TestCase):
    """Tests for CustomerManager.display_info."""

    def setUp(self):
        self.mgr = CustomerManager()

    def test_display_info_format(self):
        customer = Customer(1, "Alice", "alice@test.com")
        info = self.mgr.display_info(customer)
        self.assertIn("Alice", info)
        self.assertIn("alice@test.com", info)
        self.assertIn("ID: 1", info)


class TestCustomerModifyInfo(unittest.TestCase):
    """Tests for CustomerManager.modify_info."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.mgr = CustomerManager(self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_modify_name(self):
        customer = self.mgr.create(
            1,
            "Alice",
            "alice@test.com",
        )
        result = self.mgr.modify_info(
            customer,
            name="Bob",
        )
        self.assertTrue(result)
        self.assertEqual(customer.name, "Bob")

    def test_modify_email(self):
        customer = self.mgr.create(
            1,
            "Alice",
            "alice@test.com",
        )
        self.mgr.modify_info(
            customer,
            email="bob@test.com",
        )
        self.assertEqual(customer.email, "bob@test.com")

    def test_modify_persists_changes(self):
        customer = self.mgr.create(
            1,
            "Alice",
            "alice@test.com",
        )
        self.mgr.modify_info(customer, name="Bob")
        loaded = self.mgr.load(1)
        self.assertEqual(loaded.name, "Bob")


class TestCustomerPersistence(unittest.TestCase):
    """Tests for Customer save/load/to_dict/from_dict."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.mgr = CustomerManager(self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_save_and_load_roundtrip(self):
        customer = Customer(1, "Alice", "alice@test.com")
        self.mgr.save(customer)
        loaded = self.mgr.load(1)
        self.assertEqual(loaded.customer_id, 1)
        self.assertEqual(loaded.name, "Alice")
        self.assertEqual(loaded.email, "alice@test.com")

    def test_load_nonexistent_returns_none(self):
        result = self.mgr.load(999)
        self.assertIsNone(result)

    def test_load_corrupt_json_returns_none(self):
        filepath = self.tmp / "customer_1.json"
        filepath.write_text("not valid json")
        result = self.mgr.load(1)
        self.assertIsNone(result)

    def test_to_dict_contains_all_fields(self):
        customer = Customer(1, "Alice", "alice@test.com")
        d = self.mgr.to_dict(customer)
        self.assertEqual(d["customer_id"], 1)
        self.assertEqual(d["name"], "Alice")
        self.assertEqual(d["email"], "alice@test.com")

    def test_from_dict_reconstructs_customer(self):
        data = {
            "customer_id": 1,
            "name": "Alice",
            "email": "alice@test.com",
        }
        customer = self.mgr.from_dict(data)
        self.assertEqual(customer.customer_id, 1)

    def test_load_missing_key_returns_none(self):
        filepath = self.tmp / "customer_1.json"
        filepath.write_text(json.dumps({"customer_id": 1}))
        result = self.mgr.load(1)
        self.assertIsNone(result)

    def test_default_storage_dir(self):
        mgr = CustomerManager()
        self.assertEqual(mgr._storage_dir, Path("."))


if __name__ == "__main__":
    unittest.main()
