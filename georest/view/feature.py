# -*- encoding: utf-8 -*-

__author__ = 'pp'

"""feature persistance resources"""
import re

import flask
from flask import current_app
from flask.views import MethodView
from flask.json import jsonify
from georest.model import (ModelError,
                           ModelNotFound,
                           ModelKeyExists,
                           ModelInvalidData)


class InvalidNamespace(Exception):
    HTTP_STATUS_CODE = 400


def check_namespace(s):
    """
    :rtype: bool
    """
    m = re.match(r'^(\w+\.)*\w+$', s)
    return bool(m)


def split_namespace(s):
    """
    """
    if not check_namespace(s):
        raise InvalidNamespace('namespace %s is invalid' % s)
    try:
        i = s.rindex('.')
    except ValueError:
        return None, s
    return s[:i], s[i+1:]


class StorageView(MethodView):
    """Basic view for handling georest.model persist operations
    """

    def get(self, long_key):
        namespace, key = split_namespace(long_key)
        obj, metadata = self.model.get(self, key, namespace=namespace)
        data = self.model.as_json(obj)
        headers = {}
        if 'etag' in metadata:
            headers['ETag']
        if 'last_modified' in metadata:
            headers['Last-Modified']

    def put(self):
        pass

    def post(self):
        pass
