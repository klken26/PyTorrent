import bencodepy
import hashlib
import struct
import socket
from typing import List
from classes import TorrentFile,BencodeInfo,BencodeTorrent,Peer
from urllib.parse import *
import urllib.request


BUFFER_SIZE = 1024

def open_file(path: str) -> TorrentFile:
    try:
        with open(path, 'rb') as f:
            decoded_dict= bencodepy.decode(f.read())
            bencodeinfo_dict = BencodeInfo(decoded_dict)
            bencode_torrent = BencodeTorrent(decoded_dict[b'announce'], bencodeinfo_dict)
            return make_torrent_file(bencode_torrent)
    except Exception as e:
        return TorrentFile(), e


def hash(info: BencodeInfo) -> bytes:
    try:
        info_bytes = bencodepy.encode(info)
        h = hashlib.sha1(info_bytes).digest()
        # Return the hash value as a byte str
        return h
    except Exception as e:
        # If there is an error, return an empty byte array and the error message
        return ""


def splitHash(info: BencodeInfo) -> List:
    temp_buf = info.Pieces
    final_arr = []
    piece_size = 20
    if (len(temp_buf) % 20 != 0):
        print(f"Received malformed pieces of length {len(temp_buf)}")
    numHashes = len(temp_buf) // 20  
    for i in range(numHashes):
        # Extract a piece of 20 bytes from the long byte string
        piece = temp_buf[i * piece_size : (i + 1) * piece_size]
        # Add the piece to the list of pieces
        final_arr.append(piece) 
    return final_arr

    
def make_torrent_file(bencode_torrent: BencodeTorrent) -> TorrentFile:
    hash_str = ""
    hash_str = hash(bencode_torrent.Info.original)
    pieceHash = splitHash(bencode_torrent.Info)
    tf = TorrentFile()
    tf.Announce = bencode_torrent.Announce
    tf.InfoHash = hash_str
    tf.PieceHashes = pieceHash
    tf.PieceLength = bencode_torrent.Info.PieceLength
    tf.Length = bencode_torrent.Info.Length
    tf.Name = bencode_torrent.Info.Name
    tf.NumberOfHashes = 0
    return tf


def buildTrackerURL(peerID: str, port: int, t: TorrentFile):
    # port given here is the port of the Peer
    # port in the announce URL is the port of the website
    peerPort = str(port)
    left_int = str(t.Length)
    final_str = ""
    temp = t.Announce
    raw_bytes = t.InfoHash
    encoded_bytes = quote(raw_bytes)
    final_str = f"""/announce?info_hash={encoded_bytes}&uploaded=0&downloaded=0&left={left_int}&peer_id={peerID}&port={peerPort}&event=started&compact=1"""
    temp_arr = temp.split(':')
    temp_arr[2] = temp_arr[2].split('/')[0]
    return temp, temp_arr[0],int(temp_arr[2],10),final_str


def process_peers(decoded_str: bytes) -> List:
    peer_size = 6  # 4 for IP, 2 for port
    num_peers = len(decoded_str) // peer_size
    if len(decoded_str) % peer_size != 0:
        raise ValueError("Received malformed peers")
    peers = []
    for i in range(num_peers):
        offset = i * peer_size
        ip_bytes = decoded_str[offset:offset+4]
        port_bytes = decoded_str[offset+4:offset+6]
        ip_str = socket.inet_ntoa(ip_bytes)
        port = struct.unpack(">H", port_bytes)[0]
        peers.append(Peer(ip_str_addr=ip_str, port=port))
    return peers


def requestPeers(peerID: str, port: int, t: TorrentFile) -> List:
    #test_str = "http://cerf.cs.umd.edu:8000/announce?info_hash=%08%6035%CF%F7%9B0%0E9o%8A%7C29%E8%0B%5EW%98&uploaded=0&downloaded=0&left=3359372&peer_id=19284102906887310628&port=12313&event=started&compact=1"
    url, ip, port, announce_url = buildTrackerURL(peerID, port, t)
    url_parts = url.split("/")
    host = url_parts[2].split(":")[0]
    # Connect to server
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    # Construct HTTP request
    request = f"GET {announce_url} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"
    # Send request to server
    s.sendall(request.encode())
    # Receive response from server
    response = recvall(s)
    # Close connection
    s.close()
    response, payload_data = response.split(b"\r\n\r\n", 1)
    print(payload_data)
    decoded_data = bencodepy.decode(payload_data)
    return process_peers(decoded_data[b'peers'])

def recvall(sock, length=1024):
    # Receive all data from socket
    data = b""
    while True:
        part = sock.recv(length)
        if not part:
            break
        data += part
    return data

if __name__ == "__main__":
    #testing parsing
    t = open_file("pg2600.txt.torrent")
    #print(t.__dict__)

    #testing tracking
    str1 = 12313 #port
    str2 = "19284102906887310628" #20 characters 
    final_arr = requestPeers(str2, str1, t)
    #see ip address
    print(f"ip-address of a peer: {final_arr[0].ip_str_addr}")
    #see port
    print(f"port of a peer: {final_arr[0].port}")
    