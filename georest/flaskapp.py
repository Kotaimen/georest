# -*- encoding: utf-8 -*-

"""
    flaskapp
    ~~~~~~~~

    Main flask app

"""

__author__ = 'kotaimen'
__date__ = '3/18/14'

import platform

from werkzeug.security import safe_join

from flask import Flask, render_template, redirect, abort, jsonify
from flask.ext.markdown import Markdown

from . import default_settings, geo, __version__


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

        # self.store = self.create_store()
        # self.model = self.create_model()

        self.init_plugins()
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

    def init_plugins(self):
        # Flask-Markdown
        Markdown(self,
                 extensions=self.config.get('MARKDOWN_EXTENSIONS'),
                 extension_configs=self.config.get(
                     'MARKDOWN_EXTENSION_CONFIGS'), )

    def init_views(self):
        @self.route('/')
        def index():
            return redirect('/describe')


        @self.route('/describe')
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
                })

