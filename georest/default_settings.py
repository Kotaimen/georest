# -*- encoding: utf-8 -*-

"""
    Default settings
"""

#
# Georest
#

DATE_FORMAT = '%a, %d %b %Y %H:%M:%S GMT'

FEATURE_EXPIRES = 10

GEOREST_GEOSTORE_CONFIG = {
    'type': 'simple'
}

GEOREST_GEOMODEL_CONFIG = {
    'type': 'simple'
}


#
# Flask-Markdown Plugin
#
MARKDOWN_EXTENSIONS = ['def_list', 'attr_list',
                       'fenced_code', 'codehilite']

MARKDOWN_EXTENSION_CONFIGS = {
    'codehilite': {'pygments_style': 'emacs',
                   # for list of styles, run: pygmentize -L styles
                   'linenums': None,  # True=always, False=never, None=auto
                   'noclasses': True,  # no RSS
    }
}
