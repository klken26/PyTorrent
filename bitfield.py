from classes import *

def has_piece(bf: Bitfield, index: int) -> bool:
    byte_index = index // 8
    offset = index % 8
    if byte_index < 0 or byte_index >= len(bf):
        return False
    return bf[byte_index] >> (7 - offset) & 1 != 0


def set_piece(bf: Bitfield, index: int) -> None:
    byte_index = index // 8
    offset = index % 8
    if byte_index < 0 or byte_index >= len(bf):
        return
    bf[byte_index] |= 1 << (7 - offset)