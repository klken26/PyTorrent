from typing import Tuple
import queue
import socket

from classes import piece_progress, piece_work, piece_result, Client, Peer
from message import send_request, send_unchoke, send_interested, send_have
from peer_communication import read_message, check_integrity
from main import qlock
from bitfield import has_piece

MAXBLOCK = 20000
MAXPEERS = 4

def downloadPiece(c: Client, pw: piece_work) -> Tuple[None, bytes]:
    progress = piece_progress(pw.index, c, bytes(pw.length), 0, 0, 0)
    
    while progress.downloaded < pw.length:
        while not(c.Choked) and (progress.backlog < MAXPEERS) and (progress.requested < pw.length):
            block_size = MAXBLOCK

            if (pw.length - progress.requested) < block_size:
                block_size = pw.length - progress.requested

            send_request(c.peer, pw.index, progress.requested, block_size)

            progress.backlog += 1
            progress.requested += block_size

        error = read_message(progress)
        #print(f"{c.peer.thread_no} Got a message. Progress buffer: " + str(progress.downloaded))
        if error is not None:
            return error, None
        
    return None, progress.buf

def startDownload(peer:Peer, infoHash: bytes, work_queue: queue.Queue, result_queue: queue.Queue) -> None:
    #instantiate new client object for downloading
    c = Client(peer = peer, 
               info_hash = infoHash, 
               choked = False,
               connection = peer.socket,
               bitfield = peer.bitfield)

    send_unchoke(c.peer)

    temp = None

    while not(work_queue.empty()):
        with qlock:
            temp = work_queue.get()

        if not(has_piece(c.Bitfield, temp.index)):
            with qlock:
                work_queue.put(temp)
            continue #skips the iteration and goes to next one
        
        dw_error, dw_buf = downloadPiece(c, temp)
        if dw_error is not None:
            work_queue.put(temp)
            return
            
        error = check_integrity(temp, dw_buf)
        if error is not None:
            with qlock:
                work_queue.put(temp)
            continue #skips the iteration and goes to next one

        send_have(c.peer, temp.index)
        r = piece_result(temp.index, dw_buf)
        with qlock:
            result_queue.put(r)
            
