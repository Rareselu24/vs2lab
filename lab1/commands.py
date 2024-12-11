from typing import Literal

Commands = Literal["GET", "GET_ALL"];

def getCommandByte(command: Commands) -> bytes:
    if command == "GET":
        return bytes([0])
    elif command == "GET_ALL":
        return bytes([1])
    else:
        raise ValueError("Command not supported")

def getCommandFromByte(data: bytes) -> Commands:
    if data == bytes([0]):
        return "GET"
    elif data == bytes([1]):
        return "GET_ALL"
    else:
        raise ValueError("Command not supported or malformed input")