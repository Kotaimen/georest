# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '6/12/14'

"""
    georest.storage.exceptions
    ~~~~~~~~~~~~~~~~~~~~~~~
    Geo Feature Storage Exceptions.
"""

class DataSourceError(Exception):
    pass


class FeatureNotFound(DataSourceError):
    pass


class VersionConflicted(DataSourceError):
    pass
