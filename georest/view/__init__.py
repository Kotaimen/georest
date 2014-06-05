# -*- encoding: utf-8 -*-

"""
    georest.view
    ~~~~~~~~~~~~~

    Restful resources
"""

import flask
from flask import current_app
from flask.views import MethodView
from flask.json import jsonify
from georest import __version__


class Describe(MethodView):
    def get(self):
        return jsonify({
            'version': __version__,
        })
