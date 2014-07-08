# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '7/3/14'

"""
    georest.storage.buckets.memcash
    ~~~~~~~~~~~~~
    TODO: description

"""
import time
from pylibmc import Client
#from memcache import Client

from ..storage import FeatureStorage
from ..bucket import FeatureBucket, Commit
from ..exceptions import StorageInternalError, DuplicatedBucket, \
    FeatureNotFound, BucketNotFound


class MemcacheFeatureStorage(FeatureStorage):
    PREFIX = 'georest_buckets'

    support_version = False

    def __init__(self, hosts):
        """ Feature storage implemented in Memcache

        :param list hosts: list of hosts
            1. Strings of the form C{"host:port"}
            2. Tuples of the form C{("host:port", weight)}
        :rtype :class:`MemcacheFeatureStorage`
        """
        self._client = Client(servers=hosts)

    def create_bucket(self, name, overwrite=False, **kwargs):
        bucket_name = self._make_bucket_name(name)

        timestamp = time.time()
        try:
            add_ok = self._client.add(key=bucket_name, val=timestamp)
        except Exception as e:
            raise StorageInternalError(message='add error', e=e)

        if not add_ok:
            if overwrite:
                try:
                    rep_ok = self._client.replace(
                        key=bucket_name, val=timestamp)
                except Exception as e:
                    raise StorageInternalError('replace error', e=e)

                if not rep_ok:
                    raise StorageInternalError(message='failed to replace')
            else:
                raise DuplicatedBucket(name)

        return MemcacheFeatureBucket(name, self._client, str(timestamp))

    def get_bucket(self, name):
        bucket_name = self._make_bucket_name(name)

        try:
            timestamp = self._client.get(bucket_name)
        except Exception as e:
            raise StorageInternalError(message='get error', e=e)

        if not timestamp:
            raise BucketNotFound(name)

        return MemcacheFeatureBucket(name, self._client, str(timestamp))

    def delete_bucket(self, name):
        bucket_name = self._make_bucket_name(name)

        try:
            delete_ok = self._client.delete(bucket_name)
        except Exception as e:
            raise StorageInternalError(message='delete error', e=e)

        if not delete_ok:
            raise BucketNotFound(name)

        return True

    def has_bucket(self, name):
        bucket_name = self._make_bucket_name(name)

        try:
            get_ok = self._client.get(bucket_name)
        except Exception as e:
            raise StorageInternalError(message='get error', e=e)

        return get_ok is not None

    def close(self):
        pass

    def _make_bucket_name(self, name):
        if isinstance(name, unicode):
            name = name.encode('utf-8')
        return '.'.join((self.PREFIX, name))


class MemcacheFeatureBucket(FeatureBucket):
    def __init__(self, name, client, prefix):
        assert isinstance(client, Client)
        FeatureBucket.__init__(self, name)
        self._client = client
        self._prefix = prefix

    def commit(self, name, mapper, parent=None):
        full_name = self._make_full_name(name)

        try:
            set_ok = self._client.set(key=full_name, val=mapper)
        except Exception as e:
            raise StorageInternalError(name, e)

        if not set_ok:
            raise StorageInternalError(name)

        commit = Commit(
            name=name, revision=None, create_at=None, expire_at=None)
        return commit

    def checkout(self, name, revision=None):
        full_name = self._make_full_name(name)

        try:
            mapper = self._client.get(full_name)
        except Exception as e:
            raise StorageInternalError(name, e)

        if not mapper:
            raise FeatureNotFound(name)

        commit = Commit(
            name=name, revision=None, create_at=None, expire_at=None)
        return commit, mapper

    def remove(self, name, parent=None):
        full_name = self._make_full_name(name)

        try:
            delete_ok = self._client.delete(full_name)
        except Exception as e:
            raise StorageInternalError(name, e)

        if not delete_ok:
            raise StorageInternalError(name)

        commit = Commit(
            name=name, revision=None, create_at=None, expire_at=None)
        return commit

    def status(self, name, revision=None):
        commit, mapper = self.checkout(name=name)
        return commit

    def _make_full_name(self, name):
        if isinstance(name, unicode):
            name = name.encode('utf-8')
        return ':'.join((self._prefix, name))



