# -*- encoding: utf-8 -*-

"""
    georest.view.base
    ~~~~~~~~~~~~~~~~~
"""

__author__ = 'kotaimen'
__date__ = '3/21/14'

import datetime

from werkzeug.http import http_date
from flask import current_app, make_response
from flask.ext.restful import Resource, abort, reqparse

from ..geo import Geometry

from ..geo.exception import GeoException, InvalidGeometry, \
    InvalidCRS
from ..store.exception import FeatureAlreadyExists, InvalidKey, \
    FeatureDoesNotExist
from .exception import InvalidGeometryOperator, IdentialGeometryError

#
# Response Helpers
#


def make_header_from_feature(feature):
    """ Generate a header using feature metadata"""
    age = current_app.config['EXPIRES']
    expires = feature.modified + datetime.timedelta(seconds=age)
    return {
        'Etag': feature.etag,
        'Date': http_date(feature.created),
        'Last-Modified': http_date(feature.modified),
        'Cache-Control': 'max-age=%d,must-revalidate' % age,
        'Expires': http_date(expires)}


def make_response_from_geometry(geometry, format_='json', srid=0, headers=None):
    """ Make a geometry response """
    assert isinstance(geometry, Geometry)

    if srid:
        try:
            geometry.transform(srid)
        except GeoException as e:
            raise InvalidCRS('Cannot transform geometry crs', e)

    if format_ == 'ewkt':
        response_data = geometry.ewkt
        content_type = 'text/plain'
    elif format_ == 'ewkb':
        response_data = str(geometry.ewkb)
        content_type = 'application/oct-stream'
    elif format_ == 'json':
        response_data = geometry.json
        content_type = 'application/json'

    response = make_response(response_data, 200)
    response.headers['Content-Type'] = content_type

    if headers is not None:
        for k, v in headers.iteritems():
            response.headers[k] = v

    return response


def throws_geo_exceptions(f):
    def decorator(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            code = 200
            if isinstance(e,
                          (InvalidGeometry, InvalidCRS,
                           InvalidGeometryOperator,
                           IdentialGeometryError,
                           InvalidKey,)):
                code = 400
            elif isinstance(e, FeatureDoesNotExist):
                code = 404
            elif isinstance(e, FeatureAlreadyExists):
                code = 409
            elif isinstance(e, GeoException):
                code = 500
            else:
                raise

            abort(code,
                  code=code,
                  message=e.message,
                  exception=e.__class__.__name__,
                  # traceback=traceback.format_tb(e.tb)
            )

    return decorator


class BaseResource(Resource):
    """ Geo resource base """

    method_decorators = [throws_geo_exceptions]

    def __init__(self):
        super(BaseResource, self).__init__()
        # Inject model
        self.model = current_app.model


class GeometryRequestParser(reqparse.RequestParser):
    def __init__(self):
        super(GeometryRequestParser, self).__init__()

        self.add_argument('format',
                          dest='format',
                          action='store',
                          location='args',
                          type=str,
                          choices=['json', 'ewkt', 'ewkb'],
                          default='json',
                          required=False)

        self.add_argument('srid',
                          dest='srid',
                          action='store',
                          location='args',
                          type=int,
                          default=0,
                          required=False)

        self.add_argument('prefix',
                          dest='prefix',
                          action='store',
                          location='args',
                          type=str,
                          default=None,
                          required=False)


class PrefixParser(reqparse.RequestParser):
    def __init__(self):
        super(PrefixParser, self).__init__()

        self.add_argument('prefix',
                          dest='prefix',
                          action='store',
                          location='args',
                          type=str,
                          default=None,
                          required=False)


class OperationRequestParser(reqparse.RequestParser):
    def __init__(self):
        super(OperationRequestParser, self).__init__()

        self.add_argument('format',
                          dest='format',
                          action='store',
                          location='args',
                          type=str,
                          choices=['json', 'ewkt', 'ewkb'],
                          default='json',
                          required=False)

        self.add_argument('srid',
                          dest='srid',
                          action='store',
                          location='args',
                          type=int,
                          default=0,
                          required=False)
