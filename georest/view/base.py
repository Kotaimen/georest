# -*- encoding: utf-8 -*-

"""
    georest.view.base
    ~~~~~~~~~~~~~~~~~
"""

__author__ = 'kotaimen'
__date__ = '3/21/14'

import datetime

from flask import current_app, make_response
from flask.ext.restful import Resource, abort, reqparse

from ..geo.exception import GeoException, InvalidGeometry, \
    InvalidCoordinateReferenceSystem
from ..store.exception import GeometryAlreadyExists, InvalidKey, \
    GeometryDoesNotExist

from ..geo import Geometry

#
# Response Helpers
#

def make_header_from_feature(feature):
    """ Generate a header using feature metadata"""
    age = current_app.config['EXPIRES']
    expires = feature.modified + datetime.timedelta(seconds=age)
    date_format = current_app.config['DATE_FORMAT']
    return {
        'Etag': feature.etag,
        'Date': feature.created.strftime(date_format),
        'Last-Modified': feature.modified.strftime(date_format),
        'Cache-Control': 'max-age=%d,must-revalidate' % age,
        'Expires': expires.strftime(date_format), }


def make_response_from_geometry(geometry, format_='json', srid=0, headers={}):
    """ Make a geometry response """
    assert isinstance(geometry, Geometry)

    if srid:
        try:
            geometry.transform(srid)
        except GeoException as e:
            raise InvalidCoordinateReferenceSystem(e)

    if format_ == 'ewkt':
        response_data = geometry.ewkt
        content_type = 'text/plain'
    elif format_ == 'ewkb':
        response_data = str(geometry.ewkb)
        content_type = 'application/oct-stream'
    if format_ == 'json':
        response_data = geometry.json
        content_type = 'application/json'

    response = make_response(response_data, 200)
    response.headers['Content-Type'] = content_type

    for k, v in headers.iteritems():
        response.headers[k] = v

    return response


def throws_geo_exceptions(f):
    def decorator(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            if isinstance(e,
                          (InvalidGeometry, InvalidCoordinateReferenceSystem)):
                abort(400, message='Invalid geometry: %s' % e.message)
            elif isinstance(e, GeometryDoesNotExist):
                abort(404, message='Key does not exist: "%s"' % e.message)
            elif isinstance(e, InvalidKey):
                abort(400, message='Invalid key: "%s"' % e.message)
            elif isinstance(e, GeometryAlreadyExists):
                abort(409, message='Geometry exists: "%s"' % e.message)
            elif isinstance(e, GeoException):
                abort(500, message='Geometry exception: "%s"' % e.message)
            else:
                raise

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
                          type=str,
                          default=0,
                          required=False)