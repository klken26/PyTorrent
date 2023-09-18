from bitfield import *
from message import *
from classes import piece_progress

def calculate_bounds_for_piece(piece_index: int, piece_length: int, length: int):
    begin = piece_index * piece_length
    end = begin + piece_length
    if end > length:
        end = length
    return begin, end

def calculate_piece_size(piece_index: int, piece_length: int, length: int) -> int:
    begin, end = calculate_bounds_for_piece(piece_index, piece_length, length)
    return end - begin

def check_integrity(pw: piece_work, buf: bytes) -> None:
    hash = hashlib.sha1(buf).digest()
    if hash != pw.hash:
        return f"Index {pw.index} failed check"
    return None

def read_message(val: piece_progress) -> None:
    msg, err = read_message_from_sock(val.client.connection)
    if msg is not None:
        msg.printmessage()
    if err is not None:
        return err
    if msg is None: # keep-alive
        return None
    if msg.id == 1: #message.MsgUnchoke
        val.client.Choked = False
    elif msg.id == 0: #message.MsgChoke:
        val.client.Choked = True
    elif msg.id == 4: #message.MsgHave:
        index, err = parse_have(msg)
        if err is not None:
            return err
        set_piece(val.client.Bitfield, index)
    elif msg.id == 7: #message.MsgPiece:
        n, temp_buf = parse_piece(val.index, val.buf, msg)
        #copy over new val to val.buf
        val.buf = temp_buf
        if err is not None:
            return err
        val.downloaded += n
        val.backlog -= 1
    return None

