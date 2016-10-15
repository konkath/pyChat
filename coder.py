import base64
import json
from _operator import xor

import sys

from lab1.enums import Encode, Header


def get_secret(prime, base, power):
    mod = 1

    i = 0
    while i < power:
        current = base * mod
        mod = current % prime
        i += 1
    return mod


def prepare_message_to_send(encode, secret, msg, sender=None):
    message = code_message(encode, True, secret, msg)
    print(sys.stderr, 'coded ' + message)
    b64_msg = base64.b64encode(bytes(message.encode()))         # base64 wants ascii
    print(sys.stderr, 'based ' + str(b64_msg))
    json_msg = json.dumps({Header.msg.value: b64_msg.decode(),  # json wants utf-8
                           Header.who.value: sender}).encode()
    print(sys.stderr, json_msg)
    return bytes(json_msg)


def handle_resp_message(encode, secret, msg):
    message = base64.b64decode(msg).decode()
    print(sys.stderr, 'unbased: ' + str(message))
    decoded = code_message(encode, False, secret, message)
    print(sys.stderr, 'decoded: ' + decoded)
    return decoded


def code_message(encode, decode, secret, msg):
    if encode is Encode.xor.value:
        coded_msg = xor_coder(secret, msg)
    elif encode is Encode.caesar.value:
        if decode:
            coded_msg = decrypt_caesar(secret, msg)
        else:
            coded_msg = encrypt_caesar(secret, msg)
    else:
        coded_msg = msg  # default encoding is none

    return coded_msg


def xor_coder(secret, msg):
    coded_msg = ""
    for m in msg:
        # str m must be casted to ascii (ord) to xor it with int
        coded_msg += chr(xor(0xFF & secret, ord(m)))

    return coded_msg


def encrypt_caesar(secret, msg):
    coded_msg = ""
    for m in msg:
        # str m must be casted to ascii (ord) to shift it by last byte of secret
        # result is normalized using modulo
        coded_msg += chr(((0xFF & secret) + ord(m)) % 0xFF)

    return coded_msg


def decrypt_caesar(secret, msg):
    coded_msg = ""
    for m in msg:
        # str m must be casted to ascii (ord) to shift it by last byte of secret
        # result is normalized using modulo
        coded_msg += chr((ord(m) - (0xFF & secret)) % 0xFF)

    return coded_msg
