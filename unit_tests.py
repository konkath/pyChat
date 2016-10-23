import unittest

from lab1.coder import is_prime, get_secret, get_closest_prime, xor_coder, encrypt_caesar, decrypt_caesar


class TestCoderMethods(unittest.TestCase):

    def test_is_prime(self):
        self.assertFalse(is_prime(4))                # small input
        self.assertTrue(is_prime(3))                 # first prime
        self.assertFalse(is_prime(2))                # small input
        self.assertFalse(is_prime(1))                # 1 shouldn't be treated as prime
        self.assertFalse(is_prime(0))                # zero
        self.assertFalse(is_prime(-1))               # negative
        self.assertTrue(is_prime(22801763489))       # big input
        self.assertFalse(is_prime(22801763490))      # big input

    def test_get_secret(self):
        self.assertEqual(get_secret(23, 5, 6), 8)    # Wiki example
        self.assertEqual(get_secret(23, 5, 15), 19)  # Wiki example
        self.assertEqual(get_secret(23, 19, 6), 2)   # Wiki example
        self.assertEqual(get_secret(23, 8, 15), 2)   # Wiki example

        with self.assertRaises(ArithmeticError):
            get_secret(4, 3, 2)     # 4 is not prime
        with self.assertRaises(ArithmeticError):
            get_secret(23, 23, 5)   # base is equal to prime
        with self.assertRaises(ArithmeticError):
            get_secret(23, 5, -5)   # power is negative
        with self.assertRaises(ArithmeticError):
            get_secret(23, 5, 0)   # power is equal to zero

    def test_get_closest_prime(self):
        self.assertEqual(get_closest_prime(0), 3)                           # zero
        self.assertEqual(get_closest_prime(1), 3)                           # 1 shouldn't be treated as prime
        self.assertEqual(get_closest_prime(3), 3)                           # prime
        self.assertEqual(get_closest_prime(22801763486), 22801763489)       # big input
        self.assertEqual(get_closest_prime(22801763489), 22801763489)       # big prime

    def test_xor_coder(self):
        self.assertEqual(xor_coder(2, ''), '')                            # empty string
        self.assertEqual(xor_coder(2, 'sample_text'), 'qcorng]vgzv')      # encode some text
        self.assertEqual(xor_coder(2, 'qcorng]vgzv'), 'sample_text')      # decode some text
        self.assertEqual(xor_coder(2, 'łżóćź'), 'ŀžñąŸ')                  # encode polish signs
        self.assertEqual(xor_coder(2, 'ŀžñąŸ'), 'łżóćź')                  # decode polish signs

    def test_encrypt_caesar(self):
        self.assertEqual(encrypt_caesar(2, ''), '')                            # empty string
        self.assertEqual(encrypt_caesar(2, 'sample_text'), 'ucorngavgzv')      # encode some text
        self.assertEqual(encrypt_caesar(2, 'łżóćź'), 'ńžõĉż')                  # encode polish signs

    def test_decrypt_caesar(self):
        self.assertEqual(decrypt_caesar(2, ''), '')                            # empty string
        self.assertEqual(decrypt_caesar(2, 'ucorngavgzv'), 'sample_text')      # decode some text
        self.assertEqual(decrypt_caesar(2, 'ńžõĉż'), 'łżóćź')                  # decode polish signs

if __name__ == '__main__':
    unittest.main()
