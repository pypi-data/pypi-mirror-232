# tej-protoc v1

`tej-protoc` v1 is a implementation of custom TEJ protocol. It is a full duplex protocol.
This protocol can be used for sending large files and messages faster.

## Installation
```shell
pip install tej-protoc
```

## Diagram

```
+-------------------------------------------------------------------+
|                        TEJ Protocol v1                            |
+-------------------------------------------------------------------+
|         Status Byte            |                                  |
|--------------------------------|           Protocol Version       |
|   Status bit  |  Custom status |              8 bits              |
|    (1 bit)    |  (7 bits)      |                                  |
+-------------------------------------------------------------------+
|                         Number of files                           |
|                           (64 bits)                               |
+-------------------------------------------------------------------+
|        'n' File length         |           'n' file data          |
|         (16 bits)              |        (from 'n' file length)    |
+-------------------------------+-----------------------------------+
|                    Repeat for number of files                     |
+-------------------------------------------------------------------+
|         Message length         |           Message data           |
|           (64 bits)            |       (from message length)      |
+-------------------------------------------------------------------+
```

## Status byte

The first bit in the status byte must be `1` and then remaining bits are the custom status bits.
Custom status bit ranges from `0 to 127`

## Example usage

### Server

Here is a simple server implementation with tej-protoc.
Create a new file named `server.py`

```python
from tej_protoc.server import TPServer
from tej_protoc import protocol


class MessageCallback(protocol.ResponseCallback):
    def connected(self, client):
        builder = protocol.BytesBuilder()
        builder.set_message(b'Hello')
        client.send(builder.bytes())

    def received(self, files, message):
        print('---- Received in server ----')
        for file in files:
            print(file.name)
        print('Message: ', message.decode())
        print('---------------------------------')


server = TPServer('localhost', 8000, MessageCallback)
server.listen()

```

You can also access the `client` object inside callback methods with `self.client`.
Your code inside the Callback class is executed everytime when the client connects and
the data is received. Once the client is connected `connected` method is called. If you want to send data when client
connects, then you can send with `client.send(builder.build())`.

To send data from client, you need to build compatible bytes array with `BytesBuilder` class.


### Client

```python

from tej_protoc.client import TPClient
from tej_protoc import protocol


class ClientCallback(protocol.ResponseCallback):
    def connected(self, client):
        builder = protocol.BytesBuilder()
        builder.set_message(b'Sending from client')
        # To upload file
        # builder.add_file('file.txt', open('file.txt', 'rb').read())
        client.send(builder.bytes())

    def receive(self, files, message):
        for file in files:
            print(f'Filename: {file.name}')
            # Other attributes: file.size, file.data

        print(f'Message: {message.decode()}')


def test_client():
    try:
        client = TPClient('localhost', 8000, ClientCallback)
        client.listen()
    except Exception as e:
        print('error', e)


test_client()
```
