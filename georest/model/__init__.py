# -*- encoding: utf-8 -*-

__author__ = 'pp'

"""
    georest.model
    ~~~~~~~~~~~~~

    model interfaces used by API
"""

# from .base import (ModelError, ModelNotFound, ModelKeyExists, ModelInvalidData)
from .base import Model
from .feature import FeatureModel
from .geometry import GeometryModel
from .properties import FeaturePropModel
