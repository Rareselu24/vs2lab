import unittest
from phone_book_controller import PhoneBookController
from faker import Faker

fake = Faker()

class TestPhoneBookController(unittest.TestCase):

    def setUp(self):
        self.controller = PhoneBookController()

    def test_initial_entries_count(self):
        """Test that the initial phone book contains 500 entries."""
        entries = self.controller.getAllEntries()
        self.assertEqual(len(entries), 500, "Initial entries count should be 500")

    def test_add_entry(self):
        """Test adding a new entry to the phone book."""
        new_entry = {
            "name": fake.name(),
            "phone_number": fake.phone_number(),
            "city": fake.city()
        }
        initial_count = len(self.controller.getAllEntries())
        self.controller.addEntry(new_entry)
        updated_count = len(self.controller.getAllEntries())

        self.assertEqual(updated_count, initial_count + 1, "Entry count should increase by 1 after adding a new entry")
        self.assertIn(new_entry, self.controller.getAllEntries(), "New entry should be in the phone book after adding")

    def test_get_entry_by_name(self):
        """Test searching for an entry by name."""
        # Add a known entry for testing
        test_name = "Test User"
        test_entry = {
            "name": test_name,
            "phone_number": fake.phone_number(),
            "city": fake.city()
        }
        self.controller.addEntry(test_entry)

        results = self.controller.getEntry(test_name)
        self.assertGreater(len(results), 0, "Should return at least one result when searching by exact name")
        self.assertIn(test_entry, results, "The test entry should be in the search results")

    def test_get_entry_by_partial_name(self):
        """Test searching for an entry with a partial name."""
        test_name = "UniqueNameUser"
        test_entry = {
            "name": test_name,
            "phone_number": fake.phone_number(),
            "city": fake.city()
        }
        self.controller.addEntry(test_entry)

        partial_query = "Unique"
        results = self.controller.getEntry(partial_query)
        self.assertGreater(len(results), 0, "Should return results for partial name match")
        self.assertIn(test_entry, results, "The test entry should be in the search results for partial name match")

    def test_get_entry_by_phone_number(self):
        """Test searching for an entry by phone number."""
        test_phone_number = "555-1234"
        test_entry = {
            "name": fake.name(),
            "phone_number": test_phone_number,
            "city": fake.city()
        }
        self.controller.addEntry(test_entry)

        results = self.controller.getEntry(test_phone_number)
        self.assertGreater(len(results), 0, "Should return at least one result when searching by exact phone number")
        self.assertIn(test_entry, results, "The test entry should be in the search results for exact phone number")

    def test_get_entry_by_city(self):
        """Test searching for an entry by city."""
        test_city = "Testville"
        test_entry = {
            "name": fake.name(),
            "phone_number": fake.phone_number(),
            "city": test_city
        }
        self.controller.addEntry(test_entry)

        results = self.controller.getEntry(test_city)
        self.assertGreater(len(results), 0, "Should return at least one result when searching by exact city")
        self.assertIn(test_entry, results, "The test entry should be in the search results for exact city")

    def test_get_entry_case_insensitivity(self):
        """Test that the search is case-insensitive."""
        test_name = "CaseInsensitive"
        test_entry = {
            "name": test_name,
            "phone_number": fake.phone_number(),
            "city": fake.city()
        }
        self.controller.addEntry(test_entry)

        results = self.controller.getEntry("caseinsensitive")
        self.assertIn(test_entry, results, "Search should be case-insensitive and return matching entry")

    def test_get_all_entries(self):
        """Test retrieving all entries."""
        entries = self.controller.getAllEntries()
        self.assertEqual(len(entries), 500, "getAllEntries should return the initial 500 entries")

if __name__ == "__main__":
    unittest.main()
