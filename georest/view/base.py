# -*- encoding: utf-8 -*-

"""
    georest.view.base
    ~~~~~~~~~~~~~~~~~
"""

__author__ = 'kotaimen'
__date__ = '3/21/14'

import datetime

from flask import current_app
from flask.ext.restful import Resource, abort

from ..store.exception import GeometryAlreadyExists, InvalidKey, GeometryDoesNotExist
from ..geo.exception import InvalidGeometry, InvalidCoordinateReferenceSystem


class BaseResource(Resource):
    """ Geo resource base """

    def __init__(self):
        super(BaseResource, self).__init__()
        # Inject model
        self.model = current_app.model

    def abort(self, e):
        """ Generate status code and error message using Exception types """
        current_app.logger.exception(e)
        # exc_type, exc_value, exc_traceback = e.exc_info
        # tb = traceback.format_exc(exc_traceback)
        if isinstance(e, (InvalidGeometry, InvalidCoordinateReferenceSystem)):
            abort(400, message='Invalid geometry: %s' % e.message)
        elif isinstance(e, GeometryDoesNotExist):
            abort(404, message='Key does not exist: "%s"' % e.message)
        elif isinstance(e, InvalidKey):
            abort(400, message='Invalid key: "%s"' % e.message)
        elif isinstance(e, GeometryAlreadyExists):
            abort(409, message='Geometry exists: "%s"' % e.message)
        else:
            raise

    def header(self, feature):
        """ Generate a header using feature metadata"""
        age = current_app.config['FEATURE_EXPIRES']
        expires = feature.modified + datetime.timedelta(seconds=age)
        date_format = current_app.config['DATE_FORMAT']
        return {
            'Etag': feature.etag,
            'Date': feature.created.strftime(date_format),
            'Last-Modified': feature.modified.strftime(date_format),
            'Cache-Control': 'max-age=%d,must-revalidate' % age,
            'Expires': expires.strftime(date_format),
        }

