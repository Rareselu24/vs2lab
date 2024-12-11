import commands
import logging
from phone_book_controller import PhoneBookController
import json

logger = logging.getLogger("vs2lab.lab1.Backend")

class Backend:
    _phoneBookController = PhoneBookController()

    def handleCommand(self, data: bytes):
        # Skip the first 16 bytes (header) and extract the command byte
        command_byte = data[0:1]  # The 17th byte is the command
        command = commands.getCommandFromByte(command_byte)  # Interpret the command
        logger.debug(f"CMD: {command}")

        # The remaining bytes after the 17th byte are the payload
        payload = data[1:]

        if command == "GET":
            logger.debug("EXEC: GET")
            if len(payload) == 0:
                raise ValueError("Query data cannot be empty")
            else:
                string_data = payload.decode("utf-8")
                logger.debug(f"GET Argument is {string_data}")
                return self._get(string_data)

        elif command == "GET_ALL":
            logger.debug("EXEC: GET_ALL")
            return self._getAll()

        else:
            raise ValueError("Command not supported")

    def _get(self, search_query: str):
        if len(search_query) == 0:
            raise ValueError("Malformed string")
        else:
            # Convert the result to JSON bytes
            entries = self._phoneBookController.getEntry(search_query)
            json_data = json.dumps(entries)

            return bytes(json_data, "utf-8")

    def _getAll(self):
        # Convert all entries to JSON bytes
        entries = self._phoneBookController.getAllEntries()
        json_data = json.dumps(entries)

        return bytes(json_data, "utf-8")
