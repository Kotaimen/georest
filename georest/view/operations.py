# -*- encoding: utf-8 -*-

__author__ = 'pp'
__date__ = '6/23/14'

"""
    georest.view.operations
    ~~~~~~~~~~~~~~~~~~~~

    operation controller
"""

from collections import namedtuple
from werkzeug.http import http_date
from werkzeug.datastructures import ETags
import flask
from flask import request
from flask import current_app
from flask.views import MethodView
from flask.json import jsonify

from .exceptions import InvalidRequest


def _split_argpath(argpath):
    """generate tokens from args

    key tokens are yielded as-is;
    literal token '~' are yielded as None
    sub-literal token `~.i` are yielded as integer
    """
    if not argpath:
        flask.abort(404)

    if argpath.endswith('/'):
        flask.abort(404)

    args = argpath.split('/')
    for arg in args:
        if arg == '~':
            yield None
        elif arg.startswith('~.'):
            try:
                i = int(arg[2:])
            except ValueError:
                raise InvalidRequest('Arg %s is not valid literal token' % arg)
            yield i
        else:
            # it's a Key
            yield arg


class OperationsView(MethodView):
    def __init__(self, operations_model, feature_model):
        self.operations_model = operations_model
        self.feature_model = feature_model

    def get(self, op_name, argpath):
        geoms = []
        for token in _split_argpath(argpath):
            if token is None or isinstance(token, int):
                raise InvalidRequest('literal tokens are not allowed in GET')
            geoms.append(self.feature_model.get(token))
        kwargs = request.args.to_dict()
        if 'srid' in kwargs:
            srid = kwargs['srid']
            try:
                kwargs['srid'] = int(srid)
            except ValueError:
                raise InvalidRequest('srid %s cannot convert to integer' % srid)
        result = self.operations_model.invoke(op_name, *geoms)
        return result

    def post(self, argpath):
        pass