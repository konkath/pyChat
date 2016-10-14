from enum import Enum


class Header(Enum):
    req = 'request'
    keys = 'keys'
    p = 'p'
    g = 'g'
    a = 'a'
    b = 'b'
    enc = 'encryption'
    msg = 'msg'
    who = 'from'


class Encode(Enum):
    none = 'none'
    xor = 'xor'
    caesar = 'caesar'
