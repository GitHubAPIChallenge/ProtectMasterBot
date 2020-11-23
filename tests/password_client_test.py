import os
import sys
sys.path.append(os.path.dirname(__file__) + '/../')
from lib import password_client as password_client

import unittest



class PasswordClientTestCase(unittest.TestCase):
    def test_generate_password_returns_dict_object(self):
        """ Evaluate generate_password() returns dict object
        :return: password and hash object as dict
        :rsample: {"password": "string", "hash": "string"}
        :rtype: dict
        """
        res = password_client.generate_password()
        self.assertTrue(type(res) is dict)

    def test_generate_password_returns_password_and_hash(self):
        """ Evaluate generate_password() returns password and hash
        :return: password and hash object as dict
        :rsample: {"password": "string", "hash": "string"}
        """
        res = password_client.generate_password()
        self.assertTrue("password" in res)
        self.assertTrue("password" in res)
        self.assertTrue("hash" in res)

    def test_generate_password_returns_password_and_hash_as_strings(self):
        """ Evaluate generate_password() returns password and hash as string object
        :return: password and hash object as dict
        :rsample: {"password": "string", "hash": "string"}
        """
        res = password_client.generate_password()
        self.assertTrue(type(res["password"]) is str)
        self.assertTrue(type(res["hash"]) is str)

    def test_validate_password_returns_true(self):
        """ Evaluate validate_password() returns true
        :return: true
        :rtype: boolean
        """
        p = password_client.generate_password()
        res = password_client.validate_password(p["password"], p["hash"])
        self.assertTrue(res is True)

    def test_validate_password_returns_false(self):
        """ Evaluate validate_password() returns false
        :return: false
        :rtype: boolean
        """
        p = password_client.generate_password()
        res = password_client.validate_password("wrongpassword", p["hash"])
        self.assertTrue(res is False)

if __name__ == '__main__':
    unittest.main()
