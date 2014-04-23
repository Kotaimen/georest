# -*- encoding: utf-8 -*-

"""
    georest.store
    ~~~~~~~~~~~~~

    Geostorage layer
"""
__author__ = 'kotaimen'
__date__ = '3/18/14'

from .memory import MemoryGeoStore

#
# Factory
#
def build_store(type='memory', **argv):
    if type == 'memory':
        return MemoryGeoStore()
    else:
        raise RuntimeError('Invalid feature store type "%s"' % type)
