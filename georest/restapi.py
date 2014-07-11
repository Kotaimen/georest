# -*- encoding: utf-8 -*-

"""
    georest.restapi
    ~~~~~~~~~~~~

    Rest API hub.
"""

import traceback
import logging

import flask

from . import geo
from . import view
from . import model


API_LOGGER = logging.getLogger('georest.restapi')


class GeoRestApi(object):
    """The API hub of georest"""

    def __init__(self, app):
        self.app = app
        self.add_resources()
        self.add_error_handler()

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
        feature_storage = self.app.feature_storage

        feature_model_config = self.app.config.get('FEATURE_MODEL', dict())
        features_model = model.FeaturesModel(feature_storage, **feature_model_config)
        geometry_model = model.GeometryModel(feature_storage, **feature_model_config)
        feature_prop_model = model.FeaturePropertiesModel(feature_storage, **feature_model_config)
        operations_model = model.OperationsModel()
        attributes_model = model.AttributesModel()

        self.add_resource(view.describe, '/describe',
                          endpoint='describe')
        self.add_resource(view.Features.as_view('features', features_model),
                          '/features',
                          '/features/<key>',
                          endpoint='features')
        self.add_resource(view.Geometry.as_view('geometry', geometry_model),
                          '/features/<key>/geometry',
                          '/geometries/<key>',
                          '/geometries',
                          '/features/geometry',
                          endpoint='geometry')
        self.add_resource(view.Properties.as_view('properties',
                                                  feature_prop_model),
                          '/features/<key>/properties',
                          endpoint='properties')
        self.add_resource(view.Operations.as_view('operations',
                                                  operations_model,
                                                  geometry_model
                                                  ),
                          '/operations',
                          '/operations/<op_name>',
                          '/operations/<op_name>/<path:arg_list>',
                          '/features/<arg_list>/geometry/attributes/<op_name>',
                          '/geometries/<arg_list>/attributes/<op_name>',
                          endpoint='operations')
        self.add_resource(view.Attributes.as_view('attributes',
                                                  attributes_model,
                                                  geometry_model),
                          '/features/<key>/geometry/attributes',
                          '/geometries/<key>/attributes')

    def add_error_handler(self):
        self.app.errorhandler(geo.GeoException)(rest_error)


def rest_error(e):
    code = getattr(e, 'HTTP_STATUS_CODE', 500)

    # log if: DEBUG or 500
    # log traceback ALWAYS
    if code >= 500:
        log = API_LOGGER.error
    else:
        log = API_LOGGER.debug

    exc_info = e.__class__, e, e.traceback

    log('%s %s', flask.request.headers.get('X-Request-Id', '-'), code,
        exc_info=exc_info)

    # response traceback only if 500 and DEBUG
    data = dict(code=code,
                message=str(e),
                exception=e.__class__.__name__
                )
    if code >= 500 and flask.current_app.config['debug'] or True:
        data['traceback'] = traceback.format_tb(e.traceback)
    response = flask.jsonify(data)
    response.status_code = code
    return response
