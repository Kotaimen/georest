# -*- encoding: utf-8 -*-

"""
    App instance specific settings
"""
import os

GEOREST_DOC_DIR = os.path.abspath('doc')

GEOREST_GEOSTORE_CONFIG = {
    'type': 'couchbase',
    'bucket': 'georest',
    'host': ['172.26.183.44', '172.26.183.27']
}

GEOREST_GEOMODEL_CONFIG = {
    'type': 'simple'
}
