from phone_book_entry import PhoneBookEntry
from typing import List
import faker

fake = faker.Faker()

class PhoneBookController:
    _entries: List[PhoneBookEntry] = [
        {
            "name": fake.name(),
            "phone_number": fake.phone_number(),
            "city": fake.city()
        }
        for _ in range(500)
    ]

    def addEntry(self, entry):
        self._entries.append(entry)

    def getEntry(self, query: str) -> List[PhoneBookEntry]:
        query = query.lower()

        return [
            entry for entry in self._entries
            if query in entry["name"].lower() or
               query in entry["phone_number"].lower() or
               query in entry["city"].lower()
        ]

    def getAllEntries(self):
        return self._entries
