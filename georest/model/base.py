__author__ = 'pp'


class ModelError(Exception):
    HTTP_STATUS_CODE = 500


class ModelNotFound(ModelError):
    HTTP_STATUS_CODE = 404


class ModelKeyExists(ModelError):
    HTTP_STATUS_CODE = 412


class ModelInvalidData(ModelError):
    HTTP_STATUS_CODE = 400


class Model(object):
    """The way to persist, (de)serialize objects
    """
    def from_primitive(self, primitive):
        """from primitive representation

        :param primitive: primitive python obj
        :returns: obj
        :raises ModelInvalidData: invalid primitive
        """
        raise NotImplementedError

    def from_str(self, serialized):
        """from string representation

        :param serialized: serialized obj
        :returns: obj
        :raises ModelInvalidData: invalid serialized
        """
        raise NotImplementedError

    def as_primitive(self, obj):
        """json-serializable python object

        :returns: literal-serialized obj
        :raises ModelInvalidData: invalid obj
        """
        raise NotImplementedError

    def as_str(self, obj):
        """to string representation

        :returns: string-serialized obj
        :raises ModelInvalidData: invalid obj
        """
        raise NotImplementedError

    def create(self, obj, namespace=None):
        """
        :arg namespace: storage namespace
        :returns: key, metadata
        :raises ModelInvalidData: invalid obj
        """
        raise NotImplementedError

    def put(self, obj, key, namespace=None, etag=None):
        """
        :arg key: storage key
        :arg namespace: storage namespace
        :arg etag: check etag consistency if provided
        :returns: metadata
        :raises ModelInvalidData: invalid obj
        :raises ModelKeyExists: etag error
        """
        raise NotImplementedError

    def get(self, key, namespace=None):
        """
        :arg key: storage key
        :arg namespace: storage namespace
        :returns: obj, metadata
        :raises ModelNotFound: no such obj
        """
        raise NotImplementedError

    # def delete(self, key, namespace=None):
    #     raise NotImplementedError
