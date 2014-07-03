# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '6/20/14'

"""
    georest.storage.bucket
    ~~~~~~~~~~~~~~~~~~~~~~
    Geo Feature Bucket Interface.
"""

from collections import namedtuple


class Commit(namedtuple('Foo', 'name revision create_at expire_at')):
    """Commit result"""
    pass


class FeatureMapper(object):
    """ Object Model of Geo Feature Bucket
    """

    def __init__(self, properties, metadata, wkt, srid):
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
    """ Geo Feature Bucket Interface
    """

    def __init__(self, bucket_name):
        self._bucket_name = bucket_name

    @property
    def bucket_name(self):
        """Get bucket name"""
        return self._bucket_name

    def commit(self, name, mapper, parent=None):
        """Put a feature data.

        Returns a :class:`Commit` object.

        If parent is provided, the commit will succeed only when the parent
        match the top revision of the named feature data.

        :param basestring name: name of the feature data.
        :param :class:`FeatureMapper` mapper: feature data.
        :param basestring parent: revision to check against.
        :rtype :class:`Commit`
        """
        raise NotImplementedError

    def checkout(self, name, revision=None):
        """Get a feature data

        Return a tuple of (:class:`Commit`, :class:`FeatureMapper`)

        if revision is provided, the specified revision of feature data
        will be returned.

        Otherwise, it will be the top revision of feature data.

        :param basestring name: name of the feature data.
        :param basestring parent: revision to check against.
        :rtype tuple(:class:`Commit`, :class:`FeatureMapper`)
        """
        raise NotImplementedError

    def remove(self, name, parent=None):
        """Delete a feature data.

        Returns a :class:`Commit` object

        If parent is provided, the remove will succeed only when the parent
        match the top revision of the named feature data.

        :param basestring name: name of the feature data.
        :param basestring parent: revision to check against.
        :rtype :class:`Commit`
        """
        raise NotImplementedError

    def status(self, name, revision=None):
        """Get the commit of a revision of a feature

        Returns the commit info of the specified revision.

        if revision is not provided, it will be the top revision.

        :param basestring name: name of the feature data.
        :rtype :class:`Commit`
        """
        raise NotImplementedError

    def head(self, name):
        """Get the top commit of a feature

        Returns the top commit of the named feature data.

        :param basestring name: name of the feature data.
        :rtype :class:`Commit`
        """
        return self.status(name)

    def make_random_name(self):
        """create a random name

        Returns a random qualified name.

        :rtype basestring
        """
        raise NotImplementedError
