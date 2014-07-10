#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
    Georest WSGI script
    ~~~~~~~~~~~~~~~~~~~

    supported environment variables:
      - GEOREST_INSTANCE_PATH: override instance_path if provided
"""

__author__ = 'kotaimen'
__date__ = '3/18/14'

import os

from georest import GeoRestApp

instance_path = os.environ.get('GEOREST_INSTANCE_PATH', None)
app = GeoRestApp(settings='settings.py', instance_path=instance_path)
application = app

if __name__ == '__main__':
    from flask.ext.runner import Runner
    Runner(app).run()
