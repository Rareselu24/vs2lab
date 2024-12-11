from phone_book_entry import PhoneBookEntry
import json
from typing import List

def deserialize_phonebook_entries(json_str: str) -> List[PhoneBookEntry]:
    try:
        data = json.loads(json_str)

        entries = []

        if isinstance(data, list):
            for item in data:
                if not all(key in item for key in ("name", "phone_number", "city")):
                    raise ValueError("JSON array entry is missing one or more required fields")

                entries.append(PhoneBookEntry(**item))

        elif isinstance(data, dict):
            if not all(key in data for key in ("name", "phone_number", "city")):
                raise ValueError("JSON is missing one or more required fields")
            entries.append(PhoneBookEntry(**data))

        else:
            raise TypeError("JSON is neither an object nor an array of objects")

        return entries

    except json.JSONDecodeError:
        print("Failed to decode JSON.")
    except ValueError as ve:
        print(f"Value error: {ve}")
    except TypeError as te:
        print(f"Type error: {te}")