#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
    flask main entry
    ~~~~~~~~~~~~~~~~
"""

__author__ = 'kotaimen'
__date__ = '3/18/14'

from georest import GeoRestApp

application = GeoRestApp(settings='settings.py')

if __name__ == '__main__':
    application.run(debug=True)