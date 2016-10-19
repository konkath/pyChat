from _operator import xor

from math import sqrt


def get_secret(prime, base, power):
    mod = 1

    i = 0
    while i < power:
        current = base * mod
        mod = current % prime
        i += 1
    return mod


def get_closest_prime(number):
    if number > 1:
        while True:
            for i in range(2, int(sqrt(number))):
                if (number % i) == 0:
                    number += 1
                    break
            else:
                print(number)
                return number
    else:
        return 1


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
