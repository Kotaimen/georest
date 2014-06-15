# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '6/3/14'

import unittest

from georest.geo.exceptions import InvalidKey
from georest.geo.key import Key


class TestKey(unittest.TestCase):
    def test_build(self):
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

    def test_build_fail(self):
        self.assertRaises(InvalidKey, Key.make_key, 'a.b.c', 'Sand')
        self.assertRaises(InvalidKey, Key.make_key, 'Snake', 'Sand~')
        self.assertRaises(InvalidKey, Key.make_key, 1, 'Sand')
        self.assertRaises(InvalidKey, Key.make_key, 'Snake', 1)
        self.assertRaises(InvalidKey, Key.build_from_qualified_name, '')
        self.assertRaises(InvalidKey, Key.build_from_qualified_name, '.')
        self.assertRaises(InvalidKey, Key.build_from_qualified_name, 'Snake.')
        self.assertRaises(InvalidKey, Key.build_from_qualified_name, '.Sand')
        self.assertRaises(InvalidKey, Key.build_from_qualified_name, 'Snake..Sand')

    def test_qualified_name(self):
        key1 = Key.build_from_qualified_name('Kettle.Black')
        self.assertEqual(key1, Key.make_key('Black', 'Kettle'))
        key2 = Key.build_from_qualified_name('Kettle.Black.Osmus')
        self.assertEqual(key2, Key.make_key('Osmus', 'Kettle.Black'))
        key3 = Key.make_key()
        self.assertEqual(str(key3), 'default.?')

    def test_getattr(self):
        key = Key.make_key(bucket='Snakes', name='Sand')
        self.assertEqual(key.bucket, 'Snakes')
        self.assertEqual(key.name, 'Sand')
        self.assertEqual(key.qualified_name, 'Snakes.Sand')

    def test_hashable(self):
        key = Key.make_key(bucket='Snakes', name='Sand')
        self.assertIsInstance(hash(key), int)


if __name__ == '__main__':
    unittest.main()
