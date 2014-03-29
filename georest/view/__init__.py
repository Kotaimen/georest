# -*- encoding: utf-8 -*-

"""
    georest.view
    ~~~~~~~~~~~~~

    Restful resources
"""

__author__ = 'kotaimen'
__date__ = '3/19/14'

from .geores import *
from .geoops import *

from flask import current_app
from flask.ext.restful import Resource
from ..geo.engine import describe

class Describe(Resource):
    def get(self):
        return {
            'engine': describe(),
            'store': current_app.model.store.describe(),
            'resources': {
                'feature': {'methods': ['GET', ]},
                'geometry': {'methods': ['GET', 'POST', 'DELETE']},
                'property': {'methods': []},
            },
            'operations': {
                'unary': sorted(UnaryGeometryOperation.OPERATIONS),
                'binary': sorted(BinaryGeometryOperation.OPERATIONS),
            }
        }



