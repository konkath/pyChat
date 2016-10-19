import base64
import json
import sys

from lab1.coder import decrypt_caesar, xor_coder, encrypt_caesar
from lab1.enums import Encode, Header


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


def receive_message(sock):
    complete_msg = ''
    while True:
        raw_msg = sock.recv(4096).decode()
        complete_msg += raw_msg

        if len(raw_msg) != 4096:
            break

    return json.loads(complete_msg)
