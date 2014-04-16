# -*- encoding: utf-8 -*-

"""
    georest.view
    ~~~~~~~~~~~~~

    Restful resources
"""

__author__ = 'kotaimen'
__date__ = '3/19/14'

from flask.ext.restful import Resource


from .geometries import *
from .operations import *
from .features import *


from ..geo.engine import describe
from .. import __version__

class Describe(Resource):

    def get(self):
        return {
            'version': __version__,
            'engine': describe(),
        }


del Resource
