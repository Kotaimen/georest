# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '4/3/14'

import time

import couchbase
import couchbase.exceptions

from ..geo import Feature, build_feature, feature2literal, literial2feature
from .base import is_key_valid, SimpleGeoStore, Capability
from .exception import InvalidKey, FeatureAlreadyExists, FeatureDoesNotExist, \
    PropertyDoesNotExist, CASConflict


class SimpleCouchbaseGeoStore(SimpleGeoStore):
    """ Uses couchbase as a key-value storage for features

    Feature are stored as geojson.  Thread safety provided by underlying
    couchbase driver.
    """

    NAME = 'couchbase'

    CAPABILITY = Capability(
        efficient_key_lookup=True,
        in_memory_cache=True,
        presistence=True,

    )

    COUNTER = '__feature_counter'

    def __init__(self,
                 bucket=None,
                 host='localhost',
                 port=8091,
                 password=None,
                 timeout=2.5,
                 retries=3):
        self._conn = couchbase.Couchbase.connect(bucket=bucket,
                                                 host=host,
                                                 port=port,
                                                 password=password,
                                                 timeout=timeout, )
        assert self._conn.connected
        assert retries > 0
        # Make a (backoff, retry) list
        self._retry = zip([0.01 * 2 ** n for n in range(retries)],
                          range(retries - 1, -1, -1))

    def describe(self):
        description = super(SimpleCouchbaseGeoStore, self).describe()
        if self._conn.connected:
            description['stats'] = self._conn.stats()
            description['libcouchbase'] = self._conn.lcb_version()
        return description

    def put_feature(self, feature, key=None, prefix=None):
        key = self._make_key(key, prefix)
        feature.key = key
        try:
            self._conn.add(key, feature2literal(feature))
        except couchbase.exceptions.KeyExistsError as e:
            ret = self._conn.get(key)
            # HACK: add() raises KeyExistsError when server is busy even if op is successful
            if ret.value['_etag'] != feature.etag:
                raise FeatureAlreadyExists(
                    message='Feature already exists: "%s"' % key, e=e)
        return feature

    def get_feature(self, key, prefix=None):
        key = self._make_key(key, prefix)
        try:
            ret = self._conn.get(key)
        except couchbase.exceptions.NotFoundError as e:
            raise FeatureDoesNotExist(
                message='Feature does not exist: "%s"' % key, e=e)
        else:
            return literial2feature(ret.value)

    def delete_feature(self, key, prefix=None):
        key = self._make_key(key, prefix)
        try:
            ret = self._conn.delete(key)
        except couchbase.exceptions.NotFoundError as e:
            raise FeatureDoesNotExist(
                message='Feature does not exist: "%s"' % key, e=e)

    def update_geometry(self, geometry, key, prefix=None):

        def updater(feature):
            feature.update_geometry(geometry)
            return feature
        try:
            return self._update_document(key, prefix, updater)
        except FeatureDoesNotExist:
            feature = build_feature(geometry)
            feature.key = key
            self._conn.set(key, feature2literal(feature))
            return feature

    def update_properties(self, properties, key, prefix=None):
        def updater(feature):
            feature.update_properties(properties)
            return feature

        return self._update_document(key, prefix, updater)

    def delete_properties(self, key, prefix=None):
        def updater(feature):
            feature.properties.clear()
            feature.recalculate()
            return feature

        return self._update_document(key, prefix, updater)

    def get_property(self, name, key, prefix=None):
        # XXX: Update property without converting to Feature object?

        key = self._make_key(key, prefix)

        ret = self._conn.get(key, quiet=True)
        if ret.value is None:
            raise FeatureDoesNotExist(
                message='Feature does not exist: "%s"' % key)
        try:
            feature = literial2feature(ret.value)
            return feature.properties[name]
        except KeyError:
            raise PropertyDoesNotExist(name)

    def delete_property(self, name, key, prefix=None):
        def updater(feature):
            try:
                del feature.properties[name]
            except KeyError:
                raise PropertyDoesNotExist(name)
            feature.recalculate()
            return feature

        return self._update_document(key, prefix, updater)


    def update_property(self, name, value, key, prefix=None):
        def updater(feature):
            feature.properties[name] = value
            feature.recalculate()
            return feature

        return self._update_document(key, prefix, updater)

    def _update_document(self, key, prefix, updater):
        """ Update a object using CAS """
        key = self._make_key(key, prefix)

        for back_off, retry in self._retry:
            ret = self._conn.get(key, quiet=True)
            if ret.value is None:
                raise FeatureDoesNotExist(
                    message='Feature does not exist: "%s"' % key)

            feature = literial2feature(ret.value)
            feature = updater(feature)
            feature.recalculate()

            try:
                self._conn.set(key, feature2literal(feature), cas=ret.cas)
            except couchbase.exceptions.KeyExistsError as e:
                if retry >= 0:
                    time.sleep(back_off)
                else:
                    raise CASConflict(message='Conflict: "%s"' % key, e=e)
            else:
                return feature

    def _make_key(self, key, prefix):
        """ Make a key with prefix """
        if key is None:
            assert prefix is not None
            # Increase atomic feature counter and retrieve current value
            # XXX: Error processing...
            ret = self._conn.incr(self.COUNTER, initial=0)
            count = ret.value
            key = '%s%d' % (prefix, count)
        elif prefix is not None:
            key = '%s%s' % (prefix, key)

        if not is_key_valid(key):
            raise InvalidKey('Invalid key: "%s"' % key)

        return key
