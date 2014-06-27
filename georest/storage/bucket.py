# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '6/20/14'


"""
    georest.storage.bucket
    ~~~~~~~~~~~~~~~~~~~~~
    Geo Feature Bucket Interface.
"""


from collections import namedtuple


class Commit(namedtuple('Foo', 'name revision parent_revision timestamp')):
    """Commit result"""
    pass


class FeatureMapper(object):
    """ Object Model of Geo Feature Bucket
    """

    def __init__(self, properties, metadata, wkt, srid):
        assert isinstance(properties, dict)
        assert isinstance(metadata, dict)

        self._properties = properties
        self._metadata = metadata
        self._wkt = wkt
        self._srid = srid


    @property
    def properties(self):
        return self._properties

    @property
    def metadata(self):
        return self._metadata

    @property
    def wkt(self):
        return self._wkt

    @property
    def srid(self):
        return self._srid


class FeatureBucket(object):
    """ Geo Feature Bucket
    """

    def __init__(self, name):
        self._name = name

    @property
    def bucket_name(self):
        """Get bucket name"""
        return self._name

    def commit(self, name, mapper, parent=None):
        """Commit a feature"""
        raise NotImplementedError

    def remove(self, name, parent=None):
        """Delete a feature"""
        raise NotImplementedError

    def head(self, name):
        """Get the top commit of a feature """
        raise NotImplementedError

    def status(self, name, revision=None):
        """Get the commit of a revision of a feature"""
        raise NotImplementedError

    def checkout(self, name, revision=None):
        """Get a feature"""
        raise NotImplementedError

    def make_random_name(self):
        """make a random feature name"""
        raise NotImplementedError
