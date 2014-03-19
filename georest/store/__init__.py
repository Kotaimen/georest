# -*- encoding: utf-8 -*-

"""
    georest.store
    ~~~~~~~~~~~~~

    Geostorage layer
"""
__author__ = 'kotaimen'
__date__ = '3/18/14'

from ..geo import Feature

#
# Mock IF
#


class VeryDumbGeoStore(object):
    def put_feature(self, feature, key=None):
        pass

    def get_feature(self, key):
        return Feature()
