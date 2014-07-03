# -*- encoding: utf-8 -*-

__author__ = 'pp'

"""
    georest.view
    ~~~~~~~~~~~~~

    Restful resources
"""
import platform

import flask
from flask import current_app
from flask.json import jsonify

from georest import __version__, geo
from .feature import Features, Geometry, Properties
from .operations import Operations, Attributes


def describe():
    return jsonify(
        {
            'version': __version__,
            'platform': {'system': platform.platform(aliased=1),
                         'python': '%s-%s' % (
                             platform.python_implementation(),
                             platform.python_version()),
                },
            'engine': geo.describe(),
            'feature_storage': current_app.feature_storage.describe(),
    })
