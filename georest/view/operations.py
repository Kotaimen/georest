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

from .. import geo

from .exceptions import InvalidRequest
from .utils import get_json_content, catcher


def _split_arg_list(arg_list):
    """generate tokens from args

    key tokens are yielded as-is;
    literal token '~' are yielded as None
    sub-literal token `~.i` are yielded as integer
    """
    if not arg_list:
        flask.abort(404)

    if arg_list.endswith('/'):
        flask.abort(404)

    args = arg_list.split('/')
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


def _get_kwargs():
    kwargs = request.args.to_dict()
    if 'srid' in kwargs:
        srid = kwargs['srid']
        try:
            kwargs['srid'] = int(srid)
        except ValueError:
            raise InvalidRequest('srid %s cannot convert to integer' % srid)
    return kwargs


def _str2bool(s):
    s = s.strip().lower()

    if not s:
        return False
    elif s.startswith('n'):
        return False
    elif s.startswith('f'):
        return False
    elif s == '0':
        return False
    return True


class Operations(MethodView):

    decorators = [catcher]

    def __init__(self, operations_model, geometry_model):
        self.operations_model = operations_model
        self.geometry_model = geometry_model

    def get(self, op_name=None, arg_list=None):
        if op_name is None:
            return jsonify(self.operations_model.describe())
        if arg_list is None:
            return jsonify(self.operations_model.describe_operation(op_name))
        geoms = self._load_geoms(arg_list)
        kwargs = _get_kwargs()
        result = self.operations_model.invoke(op_name, *geoms, **kwargs)
        return result.json(), 200, {'Content-Type': 'application/json'}

    def post(self, op_name=None, arg_list=None):
        if op_name is None or arg_list is None:
            flask.abort(404)
        data = get_json_content()
        geom = geo.Geometry.build_geometry(data)
        geoms = self._load_geoms(arg_list, geom)
        kwargs = _get_kwargs()
        result = self.operations_model.invoke(op_name, *geoms, **kwargs)
        return result.json(), 200, {'Content-Type': 'application/json'}

    def _load_geoms(self, arg_list, input_geom=None):
        geoms = []
        for token in _split_arg_list(arg_list):
            if token is None:
                if input_geom is None:
                    raise InvalidRequest('Want literal tokens? use POST')
                geoms.append(input_geom)
            elif isinstance(token, int):
                if input_geom is None:
                    raise InvalidRequest('Want literal tokens? use POST')
                try:
                    sub_geom = input_geom[token]
                except (IndexError, TypeError):
                    raise InvalidRequest(
                        'literal token ~.%s is invalid' % token)
                sub_geom = geo.Geometry.build_geometry(sub_geom,
                                                       srid=input_geom.crs.srid)
                geoms.append(sub_geom)
            else:
                geom, metadata = self.geometry_model.get(token)
                geoms.append(geom)

        return geoms


class Attributes(MethodView):
    """get all useful attributes at once"""

    decorators = [catcher]

    def __init__(self, attributes_model, geometry_model):
        self.attributes_model = attributes_model
        self.geometry_model = geometry_model

    def get(self, key):
        kwargs = _get_kwargs()
        includes = []
        excludes = []
        for k, v in kwargs.items():
            if k.startswith('include_') and _str2bool(v):
                includes.append(k[8:])
                del kwargs[k]
            elif k.startswith('exclude_') and _str2bool(v):
                excludes.append(k[8:])
                del kwargs[k]

        geometry, metadata = self.geometry_model.get(key)
        result = self.attributes_model.attributes(geometry,
                                                  includes=includes,
                                                  excludes=excludes, **kwargs)
        return result, 200, {'Content-Type': 'application/json'}
