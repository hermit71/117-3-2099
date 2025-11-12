import struct

def int_to_word(value: int) -> int:
    # Преобразует signed int16 (-32768..32767) в unsigned WORD (0..65535)
    return struct.unpack('>H', struct.pack('>h', value))[0]