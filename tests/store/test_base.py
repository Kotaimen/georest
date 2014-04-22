# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '4/22/14'

import unittest

from georest.store.base import is_key_valid


class TestIsKeyValid(unittest.TestCase):
    def test_valid(self):
        self.assertTrue(is_key_valid('foo'))
        self.assertTrue(is_key_valid('foo.bar.baz'))
        self.assertTrue(is_key_valid('foo-bar-baz'))
        self.assertTrue(is_key_valid('foo_bar_baz'))

    def test_invalid(self):
        self.assertFalse(is_key_valid('geometry'))
        self.assertFalse(is_key_valid('a b c'))
        self.assertFalse(is_key_valid(''))
        self.assertFalse(is_key_valid('_foo_bar_baz'))


if __name__ == '__main__':
    unittest.main()

