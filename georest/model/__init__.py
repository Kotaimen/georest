# -*- encoding: utf-8 -*-

__author__ = 'pp'

"""
    georest.model
    ~~~~~~~~~~~~~

    Model abstraction MVC style.

    it is splitted into 3 different parts:
      - feature: feature persistent/representation interface
      - ops: operation access interface
      - query: query interface

    As it is designed as a thin-wrapper that simplify things for views,
    for now, it's not a full-capsulation of geo and storage interfaces.
    feature-objects and geometry-objects are returned as-is, and exceptions
    will pass-through, unless special handling is required.
"""

from .feature import FeatureModel, GeometryModel, FeaturePropModel
