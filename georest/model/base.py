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
    def from_pod(self, pod):
        """load obj from json-serializable python-old-data representation

        :param primitive: primitive python obj
        :returns: obj
        :raises ModelInvalidData: invalid primitive
        """
        raise NotImplementedError

    def from_json(self, serialized):
        """load obj from json representation

        :param serialized: serialized obj
        :returns: obj
        :raises ModelInvalidData: invalid serialized
        """
        raise NotImplementedError

    def as_pod(self, obj):
        """json-serializable python object

        :returns: literal-serialized obj
        :raises ModelInvalidData: invalid obj
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
