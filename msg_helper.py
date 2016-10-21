import base64
import json

from lab1.coder import decrypt_caesar, xor_coder, encrypt_caesar
from lab1.enums import Encode, Header


def prepare_message_to_send(encode, secret, msg, sender=None):
    message = code_message(encode, True, secret, msg)
    b64_msg = base64.b64encode(bytes(message.encode()))         # base64 wants ascii
    json_msg = json.dumps({Header.msg.value: b64_msg.decode(),  # json wants utf-8
                           Header.who.value: sender}).encode()
    return bytes(json_msg)


def handle_resp_message(encode, secret, msg):
    message = base64.b64decode(msg).decode()
    decoded = code_message(encode, False, secret, message)
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
        try:
            raw_msg = sock.recv(4096).decode()
        except ConnectionResetError or ConnectionAbortedError:
            raise ConnectionError      # propagate exception to thread

        complete_msg += raw_msg

        if len(raw_msg) != 4096:
            break

    return json.loads(complete_msg)
