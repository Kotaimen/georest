# -*- encoding: utf-8 -*-

__author__ = 'pp'

"""base class(es) of models"""

# class ModelError(Exception):
#     HTTP_STATUS_CODE = 500
#
#
# class ModelNotFound(ModelError):
#     HTTP_STATUS_CODE = 404
#
#
# class ModelKeyExists(ModelError):
#     HTTP_STATUS_CODE = 412
#
#
# class ModelInvalidData(ModelError):
#     HTTP_STATUS_CODE = 400


class Model(object):
    """The way to persist, (de)serialize objects

    For now, this model is meant to be a thin-wrapper. All Exceptions are
    simply forwarded from georest.geo.exception and georest.store.exception
    """
    def __init__(self, api):
        self.api = api

    def from_json(self, s):
        """load obj from json representation

        :param s: serialized obj
        :returns: obj
        :raises ModelInvalidData: invalid serialized
        """
        raise NotImplementedError

    def as_json(self, obj):
        """to string representation

        :returns: string-serialized obj
        :raises ModelInvalidData: invalid obj
        """
        raise NotImplementedError

    def create(self, obj, bucket=None):
        """create an obj in storage without giving the key

        :param bucket: storage bucket
        :returns: key, metadata
        :raises ModelInvalidData: invalid obj
        """
        raise NotImplementedError

    def put(self, obj, key, bucket=None, etag=None):
        """upadte an storage object

        :param key: storage key
        :param bucket: storage bucket
        :param etag: check etag consistency if provided
        :returns: metadata
        :raises ModelInvalidData: invalid obj
        :raises ModelKeyExists: etag error
        """
        raise NotImplementedError

    def get(self, key, bucket=None):
        """get the object by key and bucket from storage

        :param key: storage key
        :param bucket: storage bucket
        :returns: obj, metadata
        :raises ModelNotFound: no such obj
        """
        raise NotImplementedError

    # def delete(self, key, namespace=None):
    #     raise NotImplementedError


class FeatureStorageMixin(object):
    """helper that have access to feature_storage"""
    @property
    def feature_storage(self):
        return self.api.feature_storage
