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

from .model import VeryDumbGeoModel
from .store import VeryDumbGeoStore

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
        self.settings = settings
        self.load_config()

        self.store = self.create_store()
        self.model = self.create_model()

        self.init_plugins()
        self.init_routes()

    def load_config(self):
        self.config.from_object(default_settings)
        self.config.from_pyfile(self.settings, silent=True)

    def create_store(self):
        return VeryDumbGeoStore()

    def create_model(self):
        return VeryDumbGeoModel(self.store)

    def init_plugins(self):
        # Flask-Restful
        api = GeoRestApi(self)
        # Flask-Markdown
        Markdown(self,
                 extensions=self.config.get('MARKDOWN_EXTENSIONS'),
                 extension_configs=self.config.get(
                     'MARKDOWN_EXTENSIONS_CONFIG'), )

    def init_routes(self):
        # Add a test route
        @self.route('/')
        def index():
            return render_template('index.html')
