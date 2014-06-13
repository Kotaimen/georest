# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '6/12/14'

from .storage import FeatureStorage, FeatureStorageResult
from .pgstorage import PostgisFeatureStorage


def build_feature_storage(**kwargs):
    return PostgisFeatureStorage(**kwargs)
