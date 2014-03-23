# -*- encoding: utf-8 -*-

"""
    georest.store
    ~~~~~~~~~~~~~

    Geostorage layer
"""
__author__ = 'kotaimen'
__date__ = '3/18/14'

from .simple import SimpleGeoStore

#
# Factory
#
def build_store(type='simple', **argv):
    if type == 'simple':
        return SimpleGeoStore()
    else:
        raise RuntimeError('Invalid feature store type "%s"' % type)
