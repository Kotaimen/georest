# -*- encoding: utf-8 -*-

__author__ = 'pp'

"""
    georest.view.feature
    ~~~~~~~~~~~~~~~~~~~~

    feature persistence resources
"""

import re

from werkzeug.http import http_date
from werkzeug.datastructures import ETags
import flask
from flask import request
from flask import current_app
from flask.views import MethodView
from flask.json import jsonify

from ..geo import GeoException


class InvalidRequest(GeoException):  # XXX: is this appropriate?
    HTTP_STATUS_CODE = 400


class StorageView(MethodView):
    """Basic view for handling georest.model persist operations
    """
    def __init__(self, model):
        super(StorageView, self).__init__()
        self.model = model

    def get(self, key=None):
        if key is None:
            flask.abort(404)

        obj, metadata = self.model.get(key)
        data = self.model.as_json(obj)

        headers = {'Content-Type': 'application/json'}
        if 'etag' in metadata:
            headers['ETag'] = ETags([metadata['etag']])
            # check if-none-match
            if request.if_none_match.contains(metadata['etag']):
                return flask.Response(status=304)

        if 'last_modified' in metadata:
            headers['Last-Modified'] = http_date(metadata['last_modified'])
            # check if-not-modified
            if request.if_modified_since \
                    and request.if_modified_since >= metadata['last_modified']:
                return flask.Response(status=304)
        return data, 200, headers

    def put(self, key=None):
        if key is None:
            flask.abort(404)

        # etag extraction
        pre_etag = None
        if request.if_match and not request.if_match.star_tag:
            try:
                pre_etag, = request.if_match.as_set()  # only 1 allowed
            except ValueError:
                raise InvalidRequest('Cannot process if_match %s' % \
                                     request.if_match)

        obj = self._extract_content()
        metadata = self.model.put(obj, key, etag=pre_etag)

        headers = {}
        r_data = dict(code=201, key=key)
        if 'etag' in metadata:
            headers['ETag'] =ETags([metadata['etag']])
            r_data['etag'] = metadata['etag']
        response = jsonify(r_data)
        response.status_code = 201
        response.headers.extend(headers)
        return response

    def post(self, key=None):
        if not key is None:
            flask.abort(404)

        bucket = request.args.get('bucket', None)

        obj = self._extract_content()

        key, metadata = self.model.create(obj, bucket=bucket)
        headers = {}
        r_data = dict(code=201, key=key)
        if 'etag' in metadata:
            headers['ETag'] = ETags([metadata['etag']])
            r_data['etag'] = metadata['etag']
        response = jsonify(r_data)
        response.status_code = 201
        response.headers.extend(headers)
        return response

    def _extract_content(self):
        # content extraction
        if request.mimetype != 'application/json':
            raise InvalidRequest('Only "application/json" supported')
        try:
            data = request.data.decode('utf-8')
        except UnicodeError:
            raise InvalidRequest('Cannot decode content with utf-8')
        obj = self.model.from_json(data)
        return obj


class Features(StorageView):
    pass


class Geometry(StorageView):
    pass


class Properties(StorageView):
    post = None  # no create bare property
    pass
