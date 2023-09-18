import socket
from typing import Tuple
import struct
from classes import Message, Peer
import errno
from torrent_parse_and_track import recvall
from struct import pack, unpack


# Sends a message to the peer
def send_message(peer: Peer, message: Message):
    # Convert the message length to a byte array in network byte order
    message_length_net = message.length.to_bytes(4, byteorder = 'big')

    # Fill in the buffer with the message length
    buffer = ''
    for i in range(4):
        # chr converts an integer to a character
        buffer += chr(message_length_net[i])

    # Send the message length to the peer
    try:
        peer.socket.send(buffer.encode("utf-8"))
    except socket.error as e:
        if e.errno == errno.EPIPE:
            # Handle "Broken Pipe" error
            print("Socket connection closed or unavailable.")
            return
        else:
            # Handle other socket errors
            print("Socket error:", e)
            return

    if message.length > 0:
        # If the message has an id, send the id to the peer
        buffer = ''
        buffer += chr(message.id)

        try:
            peer.socket.send(buffer.encode("utf-8"))
        except socket.error as e:
            if e.errno == errno.EPIPE:
                # Handle "Broken Pipe" error
                print("Socket connection closed or unavailable.")
                return
            else:
                # Handle other socket errors
                print("Socket error:", e)
                return

        if message.length > 1:
            # If the message has a payload, send the payload to the peer
            try:
                peer.socket.send(message.Payload)
            except socket.error as e:
                if e.errno == errno.EPIPE:
                    # Handle "Broken Pipe" error
                    print("Socket connection closed or unavailable.")
                    return
                else:
                    # Handle other socket errors
                    print("Socket error:", e)
                    return

# Send a Keep Alive message to the peer
def send_keep_alive(peer:Peer):
    send_message(peer, Message(0, 0, b''))

# Send a Choke message to the peer
def send_choke(peer:Peer):
    peer.choking_peer = True
    send_message(peer, Message(1, 0, b''))

# Send an Unhoke message to the peer
def send_unchoke(peer:Peer):
    peer.choking_peer = False
    send_message(peer, Message(1, 1, b''))

# used during handshake 
def recv_unchoke(peer:Peer):
    msg = recv_message(peer)
    if (msg is None):
        print("no message received in recv_unchoke")
        return None 
    if (msg.id != 1):
        print("error: funky message received! expected id = 1. Got id = " + str(msg.id))
        return None
    peer.choked_by_peer = False

#used to receive the peer's bitfield during the handshake
def recv_bitfield(peer:Peer):
    msg = recv_message(peer)
    if (msg is None):
        print("No message received in recv_bitfield")
        return None
    if (msg.id != 5): 
        print("wrong message id in recv_bitfield. Expected 5, got id = " + str(msg.id))
        print_byte_array(msg.Payload)
    peer.bitfield = msg.Payload

# Send an Interested message to the peer
def send_interested(peer:Peer):
    peer.interested_in_peer = True
    send_message(peer, Message(1, 2, b''))

# Send a Not Interested message to the peer
def send_not_interested(peer:Peer):
    peer.interested_in_peer = False
    send_message(peer, Message(1, 3, b''))

def send_have(peer:Peer, piece_index):
    # Convert the piece index to a byte array in network byte order

    # Create the Have message with length 5, id 4, and initially empty payload
    message = Message(5, 4, b'')

    # fill in the payload with the piece index
    message.Payload = struct.pack('!I', piece_index)

    # Send the Have message to the peer
    send_message(peer, message)

# Send a Bitfield message to the peer
def send_bitfield(peer:Peer, bitfield):
    send_message(peer, Message(1 + len(bitfield), 5, bitfield))

def print_message(self):
    print("Message: <len = " + str(self.length) + "><id = " + str(self.id) + "><" + str(self.Payload) + ">")

# Send a Request message to the peer
'''
def send_request(peer:Peer, index, begin, length):
    # Convert index, begin, and length to byte arrays in network byte order
    index_net = index.to_bytes(4, byteorder = 'big')
    begin_net = begin.to_bytes(4, byteorder = 'big')
    length_net = length.to_bytes(4, byteorder = 'big')

    # Create the Request message with length 5, id 6, and initially empty payload
    message = Message(13, 6, '')

    # Append index, begin, and length to the payload
    for i in range(4):
        message.payload += chr(index_net[i])
    for i in range(4):
        message.payload += chr(begin_net[i])
    for i in range(4):
        message.payload += chr(length_net[i])

    # Send the Request message to the peer
    print_message(message)
    send_message(peer, message)
'''

def send_request(peer:Peer, index, begin, length):
    message = Message(13, 6, b'')
    message.Payload = struct.pack(
        '!III',
        index,
        begin,
        length
    )

    send_message(peer, message)

# Send a Piece message to the peer
def send_piece(peer:Peer, index, begin, block):
    # Convert index and begin to byte arrays in network byte order
    index_net = index.to_bytes(4, byteorder = 'big')
    begin_net = begin.to_bytes(4, byteorder = 'big')

    # Create the Piece message with length 9 + the length of the block, id 7, and initially empty payload
    message = Message(9 + len(block), 7, '')

    # Append index and begin to the payload
    for i in range(4):
        message.Payload += chr(index_net[i])
    for i in range(4):
        message.Payload += chr(begin_net[i])

    # Append the block to the payload
    message.Payload += block

    # Send the Piece message to the peer
    send_message(peer, message)

# Processes a Keep Alive message received from the peer
def process_keep_alive_message(peer):
    0

# Processes a Choke message received from the peer
def process_choke_message(peer):
    peer.choked_by_peer = True

# Processes an Unchoke message received from the peer
def process_unchoke_message(peer):
    peer.choked_by_peer = False

# Processes an Interested message received from the peer
def process_interested_message(peer):
    peer.peer_interested = True

# Processes a Not Interested message received from the peer
def process_not_interested_message(peer):
    peer.peer_interested = False

# Processes a Have message received from the peer
def process_have_message(peer, piece_index):
    0

# Processes a Bitfield message received from the peer
def process_bitfield_message(peer, bitfield):
    0

# Processes a Request message received from the peer
def process_request_message(peer, index, begin, length):
    0

# Processes a Piece message received from the peer
def process_piece_message(peer, index, begin, block):
    0

def recv_message(peer: Peer):
    # Stores the received message
    message = Message(0, 0, b'')

    # Receive the length from the peer and store it into the buffer
    id_buf = peer.socket.recv(4)

    # Extract the message length, in network byte order, from the buffer
    message.length = struct.unpack(">I", id_buf)[0]

    if message.length > 0:
        # If the message's length is greater than zero, the message has an id

        # Receive the byte containing the id from the peer
        buffer = peer.socket.recv(1)

        # Convert the id to an integer
        message.id = buffer[0]

        if message.length > 1:
            # If the message's length is greater than one, the message has a payload

            # Receive the payload from the peer
            message.Payload = peer.socket.recv(message.length - 1)

    # Return the message
    return message

def receive_and_process_message(peer:Peer):
    message = recv_message(peer)

    if message.length == 0:
        # If the message's length is zero, it's a Keep Alive message
        process_keep_alive_message()
    else:
        # If the message's length is not zero, it has an id

        # Which type of message is it?
        if message.id == 0:
            process_choke_message(peer)
        # TODO process rest of the messages


def read_message_from_sock(sock: socket.socket):
    # Stores the received message
    message = Message(0, 0, b'')
    # Receive the length from the peer and store it into the buffer
    timeout = 5
    sock.settimeout(timeout)
    id_buf = 0

    id_buf = sock.recv(4)
    
    # Extract the message length, in network byte order, from the buffer
    message.length = struct.unpack(">I", id_buf)[0]
    if message.length == 0:
        return None, None
    # If the message's length is greater than zero, the message has an id
    # Receive the byte containing the id from the peer
    buffer : bytes = sock.recv(1)
    # Convert the id to an integer
    message.id = int(struct.unpack("B", buffer)[0])
    if message.length > 1:
        # If the message's length is greater than one, the message has a payload
        # Receive the payload from the peer
        data_len = message.length - 1
        while len(message.Payload) < data_len:
            remaining = data_len - len(message.Payload)
            data = sock.recv(remaining)
            if not data:
                #connection lost
                break
            message.Payload += data
    return message, None
        

def parse_have(msg: Message) -> Tuple[int, None]:
    if msg.id != 4:
        raise ValueError(f"Expected HAVE (ID {4}), got ID {msg.id}")
    if len(msg.Payload) != 4:
        raise ValueError(f"Expected payload length 4, got length {len(msg.Payload)}")
    index = struct.unpack('>I', msg.Payload)[0]
    return index, None

def parse_piece(index: int, buf: bytes, msg: Message) -> Tuple[int, bytes]:

    if msg.id != 7:
        return 0, b'', ValueError(f"Expected PIECE (ID {7}), got ID {msg.id}")
    
    if len(msg.Payload) < 8:
        return 0, b'', ValueError(f"Payload too short. {len(msg.Payload)} < 8")
    
    parsedIndex = struct.unpack('>I', msg.Payload[:4])[0]
    if parsedIndex != index:
        return 0, b'', ValueError(f"Expected index {index}, got {parsedIndex}")    
    
    begin = struct.unpack('>I', msg.Payload[4:8])[0]
    if begin >= len(buf):
        return 0, b'', ValueError(f"Begin offset too high. {begin} >= {len(buf)}")
    
    data = msg.Payload[8:]
    if begin+len(data) > len(buf):
        return 0, b'', ValueError(f"Data too long [{len(data)}] for offset {begin} with length {len(buf)}")

    buf = bytearray(buf)
    buf[begin:begin+len(data)] = data
    return len(data), bytes(buf)


def print_byte_array(byte_array):
    for byte in byte_array:
        print(hex(byte)[2:].zfill(2), end=' ')
    print()  # Print a new line at the end
