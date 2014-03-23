# -*- encoding: utf-8 -*-

"""
    flaskapp
    ~~~~~~~~

    Main flask app

"""

__author__ = 'kotaimen'
__date__ = '3/18/14'

from flask import Flask, render_template
from flask.ext.markdown import Markdown

from . import default_settings

from .model import build_model
from .store import build_store

from .restapi import GeoRestApi


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

        self.store = self.create_store()
        self.model = self.create_model()

        self.init_plugins()
        self.init_views()

    def load_config(self, settings):
        # Load default settings first
        self.config.from_object(default_settings)
        if isinstance(settings, dict):
            # Load setting from a dict
            self.config.from_object(settings)
        else:
            # Load setting from instance config
            self.config.from_pyfile(settings, silent=True)

    def create_store(self):
        return build_store(**self.config['GEOREST_GEOSTORE_CONFIG'])

    def create_model(self):
        return build_model(store=self.store, **self.config['GEOREST_GEOMODEL_CONFIG'])

    def init_plugins(self):
        # Flask-Markdown
        Markdown(self,
                 extensions=self.config.get('MARKDOWN_EXTENSIONS'),
                 extension_configs=self.config.get(
                     'MARKDOWN_EXTENSIONS_CONFIG'), )

        # Flask-Restful
        api = GeoRestApi(self)

    def init_views(self):
        # Add a test route
        @self.route('/')
        def index():
            return render_template('index.html')
