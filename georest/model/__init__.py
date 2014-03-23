# -*- encoding: utf-8 -*-

"""
    georest.model
    ~~~~~~~~~~~~~

    Defines application logic

"""
__author__ = 'kotaimen'
__date__ = '3/18/14'

from .simple import SimpleGeoModel

#
# Factory
#

def build_model(store, type='simple', **args):
    if type == 'simple':
        return SimpleGeoModel(store=store)
    else:
        raise RuntimeError('Unknown geomodel type "%s"' % type)