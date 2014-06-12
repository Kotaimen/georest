# -*- encoding: utf-8 -*-

__author__ = 'pp'

"""feature persistance resources"""
import re

import flask
from flask import request
from flask import current_app
from flask.views import MethodView
from flask.json import jsonify


class InvalidRequest(Exception):
    HTTP_STATUS_CODE = 400


def check_namespace(s):
    """check if s is valid namespace

    :rtype: bool
    """
    if s is None:
        return True

    m = re.match(r'^(\w+\.)*\w+$', s)
    return bool(m)


def split_long_key(s):
    """Split the long key into bucket and key
    """
    if not (s and check_namespace(s)):
        raise InvalidRequest('key %s is invalid' % s)

    return ([None] + s.rsplit('.', 1))[-2:]


class StorageView(MethodView):
    """Basic view for handling georest.model persist operations
    """
    def get(self, long_key=None):
        if long_key is None:
            flask.abort(404)

        bucket, key = split_long_key(long_key)

        obj, metadata = self.model.get(key, bucket=bucket)
        data = self.model.as_json(obj)

        headers = {'Content-Type': 'application/json'}
        if 'etag' in metadata:
            headers['ETag'] = metadata['etag']
            # check if-none-match
            if request.if_none_match.contains(metadata['etag']):
                return flask.Response(status=304)

        if 'last_modified' in metadata:
            headers['Last-Modified'] = metadata['last_modified']
            # check if-not-modified
            if request.if_modified_since \
                    and request.if_modified_since >= metadata['last_modified']:
                return flask.Response(status=304)
        return data, 200, headers

    def _extract_content(self):
        # content extraction
        if request.mimetype != 'application/json':
            raise InvalidRequest('Only "appliaction/json" supported')
        try:
            data = request.data.decode('utf-8')
        except UnicodeError:
            raise InvalidRequest('Cannot decode content with utf-8')
        obj = self.model.from_json(data)
        return obj

    def put(self, long_key=None):
        if long_key is None:
            flask.abort(404)

        bucket, key = split_long_key(long_key)

        # etag extraction
        pre_etag = None
        if request.if_match and not request.if_match.star_tag:
            try:
                pre_etag, = request.if_match.as_set()  # only 1 allowed
            except ValueError:
                raise InvalidRequest('Cannot process if_match %s' % \
                                     request.if_match)

        obj = self._extract_content()
        metadata = self.model.put(obj, key, bucket=bucket, etag=pre_etag)

        headers = {}
        r_data = dict(code=201, key=long_key)
        if 'etag' in metadata:
            headers['ETag'] = metadata['etag']
            r_data['etag'] = metadata['etag']
        response = jsonify(code=201, key=long_key)
        response.headers.update(headers)
        return response

    def post(self, long_key=None):
        if not long_key is None:
            flask.abort(404)

        bucket = request.args.get('bucket', None)
        if not check_namespace(bucket):
            raise InvalidRequest('bucket %s is invalid' % bucket)

        obj = self._extract_content()

        key, metadata = self.model.create(obj, bucket=bucket)
        assert re.match(r'^\w+$', key)

        long_key = bucket + '.' + key if bucket else key
        headers = {}
        r_data = dict(code=201, key=long_key)
        if 'etag' in metadata:
            headers['ETag'] = metadata['etag']
            r_data['etag'] = metadata['etag']
        response = jsonify(code=201, key=long_key)
        response.headers.update(headers)
        return response


class Features(StorageView):
    @property
    def model(self):
        return current_app.feature_model


class Geometry(StorageView):
    @property
    def model(self):
        return current_app.geometry_model


class Properties(StorageView):
    post = None  # no create bare property

    @property
    def model(self):
        return current_app.feature_prop_model
