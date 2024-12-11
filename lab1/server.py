import logging
import socket
import const_cs
from backend import Backend
from context import lab_logging

lab_logging.setup(stream_level=logging.DEBUG)

class Server:
    _logger = logging.getLogger("vs2lab.lab1.Server")
    _serving = True
    _backend = Backend()

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((const_cs.HOST, const_cs.PORT))
        self.sock.settimeout(3)
        self._logger.info("Server bound to socket " + str(self.sock))

    def serve(self):
        """ Serve with a fixed 16-byte header indicating the payload size """
        self.sock.listen(1)
        while self._serving:
            try:
                (connection, address) = self.sock.accept()
                while True:
                    # First, read the 16-byte header for the incoming payload size
                    header = self._recv_exact(connection, 16)
                    if not header:
                        self._logger.error("Failed to read the payload size header.")
                        break

                    # Convert the 16-byte header to an integer representing the payload size
                    payload_size = int.from_bytes(header, byteorder='big')
                    self._logger.debug(f"Expected payload size: {payload_size} bytes")

                    # Receive the remaining data based on the payload size
                    payload = self._recv_exact(connection, payload_size)
                    if not payload:
                        self._logger.error("Failed to receive the full payload.")
                        break

                    # Process the received payload
                    response_payload = self._backend.handleCommand(payload)

                    # Prepare the response with a 16-byte header
                    response_size = len(response_payload)
                    response_header = response_size.to_bytes(16, byteorder='big')
                    response = response_header + response_payload

                    # Send the complete response back to the client
                    connection.sendall(response)

                connection.close()
            except socket.timeout:
                pass
        self.sock.close()
        self._logger.info("Server down.")

    def _recv_exact(self, connection, num_bytes: int) -> bytes:
        """ Helper function to receive exactly num_bytes from the socket """
        data = bytearray()
        while len(data) < num_bytes:
            packet = connection.recv(num_bytes - len(data))
            if not packet:
                break  # Connection closed by client
            data.extend(packet)
        return bytes(data)

server = Server()
server.serve()
