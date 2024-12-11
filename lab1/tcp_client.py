import logging
import socket
import const_cs
from commands import Commands, getCommandByte
from phone_book_entry import PhoneBookEntry
from typing import List
from json_helper import deserialize_phonebook_entries

class TcpClient:
    """ The client """
    logger = logging.getLogger("vs2lab.lab1.TcpClient")

    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((const_cs.HOST, const_cs.PORT))
        self.logger.debug("TcpClient connected to socket " + str(self.socket))

    def sendCommand(self, command: Commands, data: str = "") -> List[PhoneBookEntry]:
        command_byte = getCommandByte(command)
        data_to_send = command_byte + data.encode("utf-8")

        lengthOfDataToSend = len(data_to_send)
        self.logger.debug(f"Length of data to send: {lengthOfDataToSend} bytes")

        data_to_send = lengthOfDataToSend.to_bytes(16, byteorder='big') + data_to_send

        # Send the data over the socket
        self.socket.sendall(data_to_send)

        # Receive response with a fixed 16-byte header indicating the payload size
        header = self._recv_exact(16)
        if not header:
            self.logger.error("Failed to read response header.")
            return b""

        payload_size = int.from_bytes(header, byteorder='big')
        self.logger.debug(f"Payload size received: {payload_size} bytes")

        payload = self._recv_exact(payload_size)

        if not payload:
            self.logger.error("Failed to read the full payload.")

        if len(payload) != payload_size:
            self.logger.error("Received payload size does not match the expected size.")

        return deserialize_phonebook_entries(payload.decode("utf-8"))

    def _recv_exact(self, num_bytes: int) -> bytes:
        """ Helper function to receive exactly num_bytes from the socket """
        data = bytearray()
        while len(data) < num_bytes:
            packet = self.socket.recv(num_bytes - len(data))
            if not packet:
                break  # Connection closed by server
            data.extend(packet)
        return bytes(data)

    def close(self):
        """ Close the socket connection """
        self.socket.close()
        self.logger.debug("TcpClient closed the connection.")
