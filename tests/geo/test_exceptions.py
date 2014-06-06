# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '5/30/14'

import unittest

from georest.geo.exceptions import GeoException

class TestExceptions(unittest.TestCase):
    def test_exception_message(self):
        e = Exception('Game')
        ge = GeoException(message='Ladder')
        self.assertEqual(ge.message, 'Ladder')

        ge = GeoException(message='Ladder', e=e)
        self.assertEqual(ge.message, 'Ladder: Game')

        ge = GeoException(e=e)
        self.assertEqual(ge.message, 'Game')

        ge = GeoException()
        self.assertIsNone(ge.message)

    def test_invalid_args(self):
        self.assertRaises(AssertionError,
                          GeoException,
                          e='Ladder')
        self.assertRaises(AssertionError,
                          GeoException,
                          message=Exception('Game'))

    def test_status_code(self):
        self.assertEqual(GeoException.HTTP_STATUS_CODE, 500)


if __name__ == '__main__':
    unittest.main()
