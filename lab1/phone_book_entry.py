from dataclasses import dataclass

@dataclass
class PhoneBookEntry:
    name: str
    phone_number: str
    city: str