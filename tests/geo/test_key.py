# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '6/3/14'

import unittest

from georest.geo.key import Key


class TestKey(unittest.TestCase):
    def test_init(self):
        key1 = Key.make_key()
        self.assertEqual(key1, ('default', None))

        key2 = Key.make_key(name='Sand')
        self.assertEqual(key2, ('default', 'Sand'))

        key3 = Key.make_key('Sand')
        self.assertEqual(key3, ('default', 'Sand'))

        key4 = Key.make_key('Sand', 'Snakes')
        self.assertEqual(key4, ('Snakes', 'Sand'))

        key5 = Key.make_key('Sand', bucket='Snakes')
        self.assertEqual(key5, ('Snakes', 'Sand'))

        key6 = Key.make_key(bucket='Snakes', name='Sand')
        self.assertEqual(key6, ('Snakes', 'Sand'))

    def test_getattr(self):
        key = Key.make_key(bucket='Snakes', name='Sand')
        self.assertEqual(key.bucket, 'Snakes')
        self.assertEqual(key.name, 'Sand')

    def test_hashable(self):
        key = Key.make_key(bucket='Snakes', name='Sand')
        self.assertIsInstance(hash(key), int)


if __name__ == '__main__':
    unittest.main()
