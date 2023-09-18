import socket
import hashlib
import sys
import secrets
import binascii
import random
import struct

from struct import pack, unpack
from typing import List
from classes import Peer
from message import *

class Handshake():
    def __init__(self, info_hash: bytes):
        self.info_hash = info_hash
        self.peer_id = self.generate_peer_id().encode("utf-8")

    def generate_peer_id(self):
        return ''.join(str(random.randint(0,9) for _ in range(20)))
    
    def pack_handshake(self) -> bytes:
        return pack(
            'B19s8x20s20s',        #format string:
            19,                         #1 byte
            b"BitTorrent protocol",     #19 bytes, followed by 8 byte padding
            self.info_hash,             #20 bytes
            self.peer_id)               #20 bytes
    
    def send_handshake(self, socket):
        socket.send(self.pack_handshake())

    def recv_handshake(self, socket) -> int:
        recv_message = socket.recv(68)
        if not(recv_message):
            return 0
        
        recv_unpack = unpack('B19s8x20s20s', recv_message)
        self.info_hash = recv_unpack[2]
        self.peer_id = recv_unpack[3]
        return 1
    
def do_handshake(peer: Peer, global_info_hash: bytes):
    # connect to the peer
    peer.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Set the timeout to 5 seconds
    timeout = .1
    peer.socket.settimeout(timeout)
    (peer.socket).connect((peer.ip_str_addr, peer.port))

    # send the handshake
    init_handshake = Handshake(global_info_hash)
    init_handshake.send_handshake(peer.socket)

    #receive the response
    response_handshake = Handshake(global_info_hash)
    Handshake.recv_handshake(response_handshake, peer.socket)

    #validate the response
    if response_handshake.info_hash != init_handshake.info_hash:
        print("Hashes don't match in do_handshake")
        return None 

    #receive the bitfield from the peer
    recv_bitfield(peer)
    #print("here's the peer's bitfield: " + str(peer.bitfield))

    #get ready for downloading
    send_interested(peer)
    recv_unchoke(peer)
