from typing import Tuple, Optional, List
import socket

from .callbacks import ResponseCallback
from .exceptions import InvalidStatusCode, InvalidProtocolVersion, ConnectionClosed, ProtocolException
from .file import File


class SocReader:
    def __init__(self, max_buffer_size: Optional[int]):
        self.max_buffer_size = max_buffer_size

        if not max_buffer_size:
            self.max_buffer_size = 8 * 1024

    def read_bytes(self, client: socket.socket, size: int) -> bytes:
        data = bytearray(size)
        # Create a memory view on the data bytearray
        memory_view = memoryview(data)

        bytes_in = 0
        buffer_size = min(size, self.max_buffer_size)

        while bytes_in != size:
            remaining_size = size - bytes_in
            max_read = min(remaining_size, buffer_size)
            chunk = client.recv(max_read)
            if not chunk:
                raise ConnectionClosed()

            # Assign the chunk to the appropriate slice in the memory view
            memory_view[bytes_in:bytes_in + len(chunk)] = chunk

            bytes_in += len(chunk)

        return bytes(data)


class FrameReader:
    def __init__(self, buffer_size: Optional[int] = None):
        self.soc_reader = SocReader(buffer_size)

    def read_status(self, client: socket.socket) -> Tuple[int, int]:
        """
        Reads first byte from the dataframe
        """

        first_byte = self.soc_reader.read_bytes(client, 1)
        status = ord(first_byte) >> 7
        custom_status = ord(first_byte) & 0b01111111
        return status, custom_status

    def read_protocol_version(self, client: socket.socket) -> int:
        return ord(self.soc_reader.read_bytes(client, 1))

    def count_number_of_files(self, client: socket.socket) -> int:
        return int.from_bytes(self.soc_reader.read_bytes(client, 8), byteorder='big')

    def read_file(self, client: socket.socket) -> Tuple[str, bytes, int]:
        filename_length = int.from_bytes(self.soc_reader.read_bytes(client, 2), byteorder='big')
        filename = self.soc_reader.read_bytes(client, filename_length).decode()
        file_length = int.from_bytes(self.soc_reader.read_bytes(client, 8), byteorder='big')
        file_data = self.soc_reader.read_bytes(client, file_length)
        return filename, file_data, file_length

    def read_message(self, client: socket.socket) -> Optional[bytes]:
        message_length = int.from_bytes(self.soc_reader.read_bytes(client, 8), byteorder='big')

        if message_length == 0:
            return None

        return self.soc_reader.read_bytes(client, message_length)


def read(client: socket.socket, callback: ResponseCallback, frame_reader: FrameReader):
    status, custom_status = frame_reader.read_status(client)
    if status != 1:
        print('Invalid starting bit. Received: ', bin(status)[2:])
        raise ProtocolException()  # First bit must be 1 to be valid

    callback.status = custom_status
    callback.protocol_version = frame_reader.read_protocol_version(client)

    files_count = frame_reader.count_number_of_files(client)

    files: List[File] = []

    for e in range(files_count):
        filename, file_data, file_size = frame_reader.read_file(client)
        files.append(File(filename, file_data, file_size))

    message = frame_reader.read_message(client)
    callback.received(files, message)
    del frame_reader


class BytesBuilder:
    """
    Constructs bytes for TEJ protocol
    """

    def __init__(self, status_code: Optional[int] = None):
        self._status_code = 0

        if status_code:
            in_range = (status_code >= 0 or status_code <= 0b01111111)
            if not in_range:
                raise InvalidStatusCode('The allowed range is 0 to 127')

            self._status_code = status_code

        self._bytearray = bytearray()
        self._protocol_version: int = 1
        self._files: List[File] = []
        self._message: Optional[bytes] = None

    def set_protocol_version(self, version: int) -> 'BytesBuilder':
        if not (version >= 0 or version <= 256):
            raise InvalidProtocolVersion('The allowed range is 0 to 256')

        self._protocol_version = version
        return self

    def add_file(self, filename: str, data: bytes):
        self._files.append(File(filename, data, len(data)))
        return self

    def set_message(self, message: bytes):
        self._message = message
        return self

    def bytes(self) -> bytes:
        self._bytearray.clear()

        # Status byte 8 bit
        status_byte = self._status_code | 0b10000000  # Set 1 to MSB
        self._bytearray.append(status_byte)

        # Protocol version 8 bit
        self._bytearray.append(self._protocol_version)

        # Files count 64 bits
        files_count = len(self._files)
        self._bytearray += files_count.to_bytes(8, byteorder='big')

        # Add files information to data frame
        for file in self._files:
            # File length 16 bit
            filename_length = len(file.name)
            self._bytearray += filename_length.to_bytes(2, byteorder='big')

            # n bits from filename length
            self._bytearray += bytes(file.name, 'utf-8')

            # file size
            file_size = len(file.data)
            file_length = file_size.to_bytes(8, byteorder='big')
            self._bytearray += file_length

            # file n bits from file size
            self._bytearray += file.data

        message_length = 0
        if self._message:
            message_length = len(self._message)

        # Message length 64 bit
        message_length = message_length.to_bytes(8, byteorder='big')
        self._bytearray += message_length

        if self._message:
            # Message n bits from message length
            self._bytearray += self._message

        return bytes(self._bytearray)
