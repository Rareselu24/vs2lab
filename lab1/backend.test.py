import unittest
from backend import Backend
from phone_book_controller import PhoneBookController
from unittest.mock import patch, MagicMock
import json

class TestBackend(unittest.TestCase):

    def setUp(self):
        """Initialize a fresh Backend instance before each test."""
        self.backend = Backend()
        self.mock_phonebook = self.backend._phoneBookController
        self.mock_get_command = b'\x01'  # Mock byte for "GET" command
        self.mock_get_all_command = b'\x02'  # Mock byte for "GET_ALL" command

    @patch('commands.getCommandFromByte')
    def test_handle_get_command(self, mock_getCommandFromByte):
        """Test handleCommand with a GET command and valid payload."""
        search_query = "Test User"
        expected_result = [{"name": search_query, "phone_number": "123456789", "city": "Testville"}]

        # Mock the behavior of commands.getCommandFromByte and phonebook search results
        mock_getCommandFromByte.return_value = "GET"
        self.mock_phonebook.getEntry = MagicMock(return_value=expected_result)

        # Prepare data with command byte and encoded query
        data = self.mock_get_command + search_query.encode('utf-8')

        # Call handleCommand
        response = self.backend.handleCommand(data)

        # Check the response matches expected JSON output
        self.assertEqual(json.loads(response.decode('utf-8')), expected_result, "GET command should return correct entry data")

    @patch('commands.getCommandFromByte')
    def test_handle_get_all_command(self, mock_getCommandFromByte):
        """Test handleCommand with GET_ALL command."""
        expected_result = [
            {"name": "Alice", "phone_number": "111111111", "city": "City1"},
            {"name": "Bob", "phone_number": "222222222", "city": "City2"}
        ]

        # Mock the behavior of commands.getCommandFromByte and phonebook getAll results
        mock_getCommandFromByte.return_value = "GET_ALL"
        self.mock_phonebook.getAllEntries = MagicMock(return_value=expected_result)

        # Prepare data with only command byte (no payload for GET_ALL)
        data = self.mock_get_all_command

        # Call handleCommand
        response = self.backend.handleCommand(data)

        # Check the response matches expected JSON output
        self.assertEqual(json.loads(response.decode('utf-8')), expected_result, "GET_ALL command should return all entries")

    @patch('commands.getCommandFromByte')
    def test_handle_get_command_empty_payload(self, mock_getCommandFromByte):
        """Test handleCommand with a GET command but empty payload, expecting ValueError."""
        mock_getCommandFromByte.return_value = "GET"

        # Prepare data with command byte but no payload
        data = self.mock_get_command

        # Assert that ValueError is raised for empty query
        with self.assertRaises(ValueError, msg="Query data cannot be empty"):
            self.backend.handleCommand(data)

    @patch('commands.getCommandFromByte')
    def test_handle_get_command_empty_search_query(self, mock_getCommandFromByte):
        """Test _get method with empty search query, expecting ValueError."""
        mock_getCommandFromByte.return_value = "GET"

        # Prepare data with command byte and empty search query
        data = self.mock_get_command + b""

        # Assert that ValueError is raised for empty query string
        with self.assertRaises(ValueError, msg="Malformed string"):
            self.backend.handleCommand(data)

    @patch('commands.getCommandFromByte')
    def test_handle_unsupported_command(self, mock_getCommandFromByte):
        """Test handleCommand with unsupported command, expecting ValueError."""
        mock_getCommandFromByte.return_value = "UNSUPPORTED"

        # Prepare data with unsupported command byte
        unsupported_command_byte = b'\x03'  # An example of unsupported byte
        data = unsupported_command_byte

        # Assert that ValueError is raised for unsupported command
        with self.assertRaises(ValueError, msg="Command not supported"):
            self.backend.handleCommand(data)

if __name__ == "__main__":
    unittest.main()
