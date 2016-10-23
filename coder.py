from _operator import xor

from math import sqrt


def is_prime(number):
    if number < 3:
        return False

    for i in range(2, int(sqrt(number)) + 1):
        if (number % i) == 0:
            return False

    return True


def get_secret(prime, base, power):
    if not is_prime(prime) or base < 1 or base >= prime or power < 1:
        raise ArithmeticError

    mod = 1

    i = 0
    while i < power:
        current = base * mod
        mod = current % prime
        i += 1
    return mod


def get_closest_prime(number):
    if number < 3:
        return 3

    while True:
        if not is_prime(number):
            number += 1
        else:
            return number


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
        # result is normalized using 2 bytes modulo (polish signs in utf-8)
        coded_msg += chr(((0xFF & secret) + ord(m)) % 0xFFFF)

    return coded_msg


def decrypt_caesar(secret, msg):
    coded_msg = ""
    for m in msg:
        # str m must be casted to ascii (ord) to shift it by last byte of secret
        # result is normalized using 2 bytes modulo (polish signs in utf-8)
        coded_msg += chr((ord(m) - (0xFF & secret)) % 0xFFFF)

    return coded_msg
