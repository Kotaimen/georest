# -*- encoding: utf-8 -*-

"""
    flaskapp
    ~~~~~~~~

    Main flask app

"""

__author__ = 'kotaimen'
__date__ = '3/18/14'

import logging.config

from flask import Flask, redirect

from . import default_settings
from .restapi import GeoRestApi
from . import storage


class GeoRestApp(Flask):
    """
        Main flask app

        Load configuration, build application model object, and install
        restful resources.
    """

    def __init__(self,
                 import_name=__package__,
                 settings='settings.py',
                 **kwargs):
        super(GeoRestApp, self).__init__(import_name,
                                         instance_relative_config=True,
                                         **kwargs)
        self.load_config(settings)
        self.init_logging()
        self.init_datasources()
        self.init_api()
        self.init_views()

    def load_config(self, settings):
        # Load default settings first
        self.config.from_object(default_settings)
        if isinstance(settings, dict):
            # Load setting from a dict
            self.config.update(settings)
        else:
            # Load setting from instance config
            self.config.from_pyfile(settings, silent=True)

    def init_datasources(self):
        self.feature_storage = storage.build_feature_storage(
            **self.config['STORAGE'])

    def init_views(self):
        """initiate extra views"""
        @self.route('/')
        def index():
            return redirect('/describe')

    def init_api(self):
        api = GeoRestApi(self)  # avoid circular reference, dont store handler

    def init_logging(self):
        cfg = self.config.get('LOGGING', None)
        if cfg:
            logging.config.dictConfig(cfg)
