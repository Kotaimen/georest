# -*- encoding: utf-8 -*-

__author__ = 'pp'
__date__ = '7/11/14'

"""
    Georest WSGI script
    ~~~~~~~~~~~~~~~~~~~

    supported environment variables:
      - GEOREST_INSTANCE_PATH: override instance_path if provided
"""

import os

from georest import GeoRestApp

instance_path = os.environ.get('GEOREST_INSTANCE_PATH', None)
app = GeoRestApp(settings='settings.py', instance_path=instance_path)
application = app
