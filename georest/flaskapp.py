# -*- encoding: utf-8 -*-

"""
    flaskapp
    ~~~~~~~~

    Main flask app

"""

__author__ = 'kotaimen'
__date__ = '3/18/14'

from flask import Flask, render_template, redirect, abort, jsonify

from . import default_settings
from .restapi import GeoRestApi
from . import storage


def render_markdown(md_file, title):
    try:
        with open(md_file) as fp:
            markdown = fp.read()
            return render_template('markdown.html', title=title,
                                   markdown=markdown)
    except IOError as e:
        abort(404)


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

        self.init_datasources()
        # self.init_models()
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
        self.feature_storage = storage.build_feature_storage()

    # def init_models(self):
    #     pass

    def init_views(self):
        """initiate extra views"""
        @self.route('/')
        def index():
            return redirect('/describe')

    def init_api(self):
        api = GeoRestApi(self)  # avoid circular reference, dont store handler
