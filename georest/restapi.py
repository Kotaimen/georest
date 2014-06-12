# -*- encoding: utf-8 -*-

"""
    georest.api
    ~~~~~~~~~~~~

    Rest API hub
"""

import traceback

import flask

from georest import geo
from georest import view
from georest import model


class GeoRestApi(object):
    """The API hub of georest"""

    def __init__(self, app):
        self.app = app
        self.init_models()
        self.add_resources()

    def init_models(self):
        # XXX: the models are stored in app, this implies circular reference
        # but it's ... simple ...
        self.app.feature_model = model.FeatureModel(self)
        self.app.feature_prop_model = model.FeaturePropModel(self)
        self.app.geometry_model = model.GeometryModel(self)

    def add_resource(self, resource, *urls, **kwargs):
        """utility method to add resources

        :param resource: flask view
        :param urls: url rules to apply
        :param kwargs: applied to app.add_url_rule as-is
        """
        for url_rule in urls:
            self.app.add_url_rule(url_rule, view_func=resource, **kwargs)

    def add_resources(self):
        """bind api urls to app"""
        self.add_resource(view.describe, '/describe',
                          endpoint='describe')
        self.add_resource(view.Features.as_view('features'),
                          '/features',
                          '/features/<long_key>',
                          endpoint='features')
        self.add_resource(view.Geometry.as_view('geometry'),
                          '/features/<long_key>/geometry',
                          '/geometries/<long_key>',
                          '/geometries',
                          '/features/geometry',
                          endpoint='geometry')
        self.add_resource(view.Properties.as_view('properties'),
                          '/features/<long_key>/properties',
                          endpoint='properties')

    def add_errorhandler(self):
        self.app.errorhandler(geo.GeoException)(rest_error)

    @property
    def feature_storage(self):
        return self.app.feature_storage


def rest_error(e):
    code = getattr(e, 'HTTP_STATUS_CODE', 500)
    response = flask.jsonify(dict(code=code,
                                  message=str(e),
                                  exception=e.__class__.__name__,
                                  traceback=traceback.format_tb(e.tb)
    ))
    response.status = code
    return response
