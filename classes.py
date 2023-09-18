import socket
import ipaddress
from typing import List
import hashlib
import struct
from typing import Tuple

class Peer:
    def __init__(self,ip=None, ip_str_addr=None, port=None, bitfield=None, thread_no=0):
        self.socket = socket.socket()
        self.ip = ip
        self.ip_str_addr = ip_str_addr
        self.port = port
        self.peer_id = ""
        self.bitfield = bitfield
        self.download_rate = 0.0
        self.upload_rate = 0.0
        self.choked_by_peer = True
        self.choking_peer = False
        self.peer_interested = False
        self.interested_in_peer = False
        self.thread_no = thread_no
    
class Message:
    def __init__(self,  length: int = 0, ID: int = 0, payload: bytes = b''):
        self.length = length
        self.id = ID
        self.Payload = payload

    def printmessage(self):
        print("Message: <len = " + str(self.length) + " ><id = " + str(self.id) + "><" + str(len(self.Payload)) + ">")

class Bitfield:
    def __init__(self, data:bytes):
        self.data = data

class piece_work:
    def __init__(self, index: int, hash:bytes, length:int):
        self.index = index
        self.hash = hash
        self.length = length

class piece_result:
    def __init__(self, index:int, buf:bytes):
        self.index = index
        self.buf = buf

class Client:
    def __init__(self, connection: socket.socket, choked: bool, bitfield: Bitfield, peer: Peer, info_hash: bytes, peer_id: str = ""):
        self.connection = connection
        self.Choked = choked
        self.Bitfield = bitfield
        self.peer = peer
        self.infoHash = info_hash
        self.peerID = peer_id

class piece_progress:
    def __init__(self, index:int, client: Client, buf:bytes, downloaded:int, requested:int, backlog:int):
        self.index = index
        self.client = client
        self.buf = buf
        self.downloaded = downloaded
        self.requested = requested
        self.backlog = backlog

class BencodeTrackerResp:
    def __init__(self):
        self.interval = 0
        self.peers = ""
        self.complete = 0
        self.incomplete = 0
        self.downloaded = 0
        self.min_interval = 0

class TorrentFile:
    def __init__(self):
        self.Announce = ""
        self.InfoHash = ""
        self.PieceHashes = []
        self.PieceLength = 0
        self.Length = 0
        self.Name = ""
        self.NumberOfHashes = 0

class BencodeInfo:
    def __init__(self,bto: dict):
        self.Pieces = bto[b'info'][b'pieces']
        self.PieceLength = bto[b'info'][b'piece length']
        self.Length = bto[b'info'][b'length']
        self.Name = bto[b'info'][b'name']
        self.original = bto[b'info']
        self.Private = 0

class BencodeTorrent:
    def __init__(self, announce_str: bytes, made_bt: BencodeInfo):
        self.Announce = announce_str.decode("utf-8")
        self.Info = made_bt

# class Torrent:
#     def __init__(self, peer: Peer, peerID: str, infoHash: bytes):
#         self.peer = peer
#         self.peerID = peerID
#         self.infoHash = infoHash
#         self.pieceHashes = []
#         self.pieceLength = 0
#         self.length = 0
#         self.name = ""
