"""Unit tests for the Customer class."""

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
from customer import Customer  # noqa: E402


class TestCustomerCreate(unittest.TestCase):
    """Tests for Customer.create class method."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_create_returns_customer(self):
        customer = Customer.create(
            1,
            "Alice",
            "alice@test.com",
            storage_dir=self.tmp,
        )
        self.assertIsNotNone(customer)
        self.assertEqual(customer.name, "Alice")

    def test_create_persists_file(self):
        Customer.create(
            1,
            "Alice",
            "alice@test.com",
            storage_dir=self.tmp,
        )
        filepath = self.tmp / "customer_1.json"
        self.assertTrue(filepath.exists())

    def test_create_save_failure_returns_none(self):
        bad_dir = self.tmp / "nonexistent" / "deep"
        customer = Customer.create(
            1,
            "Alice",
            "alice@test.com",
            storage_dir=bad_dir,
        )
        self.assertIsNone(customer)


class TestCustomerDelete(unittest.TestCase):
    """Tests for Customer.delete method."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_delete_removes_file(self):
        customer = Customer.create(
            1,
            "Alice",
            "alice@test.com",
            storage_dir=self.tmp,
        )
        result = customer.delete()
        self.assertTrue(result)
        self.assertFalse((self.tmp / "customer_1.json").exists())

    def test_delete_nonexistent_returns_false(self):
        customer = Customer(1, "Alice", "alice@test.com")
        customer._storage_dir = self.tmp
        result = customer.delete()
        self.assertFalse(result)


class TestCustomerDisplayInfo(unittest.TestCase):
    """Tests for Customer.display_info method."""

    def test_display_info_format(self):
        customer = Customer(1, "Alice", "alice@test.com")
        info = customer.display_info()
        self.assertIn("Alice", info)
        self.assertIn("alice@test.com", info)
        self.assertIn("ID: 1", info)


class TestCustomerModifyInfo(unittest.TestCase):
    """Tests for Customer.modify_info method."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_modify_name(self):
        customer = Customer.create(
            1,
            "Alice",
            "alice@test.com",
            storage_dir=self.tmp,
        )
        result = customer.modify_info(name="Bob")
        self.assertTrue(result)
        self.assertEqual(customer.name, "Bob")

    def test_modify_email(self):
        customer = Customer.create(
            1,
            "Alice",
            "alice@test.com",
            storage_dir=self.tmp,
        )
        customer.modify_info(email="bob@test.com")
        self.assertEqual(customer.email, "bob@test.com")

    def test_modify_persists_changes(self):
        customer = Customer.create(
            1,
            "Alice",
            "alice@test.com",
            storage_dir=self.tmp,
        )
        customer.modify_info(name="Bob")
        loaded = Customer.load(1, storage_dir=self.tmp)
        self.assertEqual(loaded.name, "Bob")


class TestCustomerPersistence(unittest.TestCase):
    """Tests for Customer save/load/to_dict/from_dict."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_save_and_load_roundtrip(self):
        customer = Customer(1, "Alice", "alice@test.com")
        customer._storage_dir = self.tmp
        customer.save()
        loaded = Customer.load(1, storage_dir=self.tmp)
        self.assertEqual(loaded.customer_id, 1)
        self.assertEqual(loaded.name, "Alice")
        self.assertEqual(loaded.email, "alice@test.com")

    def test_load_nonexistent_returns_none(self):
        result = Customer.load(999, storage_dir=self.tmp)
        self.assertIsNone(result)

    def test_load_corrupt_json_returns_none(self):
        filepath = self.tmp / "customer_1.json"
        filepath.write_text("not valid json")
        result = Customer.load(1, storage_dir=self.tmp)
        self.assertIsNone(result)

    def test_to_dict_contains_all_fields(self):
        customer = Customer(1, "Alice", "alice@test.com")
        d = customer.to_dict()
        self.assertEqual(d["customer_id"], 1)
        self.assertEqual(d["name"], "Alice")
        self.assertEqual(d["email"], "alice@test.com")

    def test_from_dict_reconstructs_customer(self):
        data = {
            "customer_id": 1,
            "name": "Alice",
            "email": "alice@test.com",
        }
        customer = Customer.from_dict(
            data,
            storage_dir=self.tmp,
        )
        self.assertEqual(customer.customer_id, 1)

    def test_load_missing_key_returns_none(self):
        filepath = self.tmp / "customer_1.json"
        filepath.write_text(json.dumps({"customer_id": 1}))
        result = Customer.load(1, storage_dir=self.tmp)
        self.assertIsNone(result)

    def test_default_storage_dir(self):
        customer = Customer(1, "Alice", "alice@test.com")
        self.assertEqual(customer._storage_dir, Path("."))


if __name__ == "__main__":
    unittest.main()
