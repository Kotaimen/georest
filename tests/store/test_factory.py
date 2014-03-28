# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '3/28/14'

from georest.store import build_store
import unittest


class TestBuildStore(unittest.TestCase):
    def test_simple(self):
        store = build_store('simple')
        self.assertIsNotNone(store)

    def test_failure(self):
        self.assertRaises(RuntimeError, build_store, 'what_ever')


if __name__ == '__main__':
    unittest.main()

