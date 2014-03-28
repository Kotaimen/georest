# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '3/27/14'

from georest.model import build_model
from georest.store import build_store
import unittest


class TestBuildModel(unittest.TestCase):
    def setUp(self):
        self.store = build_store('simple')

    def test_simple(self):
        model = build_model(self.store, 'simple')
        self.assertIsNotNone(model)

    def test_failure(self):
        self.assertRaises(RuntimeError, build_model, self.store, 'what_ever')


if __name__ == '__main__':
    unittest.main()

