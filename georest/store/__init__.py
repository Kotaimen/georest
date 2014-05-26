# -*- encoding: utf-8 -*-

"""
    georest.store
    ~~~~~~~~~~~~~

    Geostorage layer
"""
__author__ = 'kotaimen'
__date__ = '3/18/14'

from .memory import MemoryGeoStore

try:
    from .couch import SimpleCouchbaseGeoStore
except ImportError:
    SimpleCouchbaseGeoStore = None

#
# Factory
#
def build_store(type='memory', **kwargs):
    if type == 'memory':
        return MemoryGeoStore()
    elif type == 'couchbase':
        return SimpleCouchbaseGeoStore(**kwargs)
    else:
        raise RuntimeError('Invalid feature store type "%s"' % type)
