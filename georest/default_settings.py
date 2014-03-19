# -*- encoding: utf-8 -*-

"""
    Default settings
"""

#
# Test
#
GEOREST_FOOBAR = False
GEOREST_FOOBAZ = False


#
# Flask-Markdown Plugin
#
MARKDOWN_EXTENSIONS = ['def_list', 'attr_list',
                       'fenced_code', 'codehilite']

MARKDOWN_EXTENSIONS_CONFIG = {
    'codehilite': {'pygments_style': 'emacs',
                   # for list of styles, run: pygmentize -L styles
                   'linenums': None,  # True=always, False=never, None=auto
                   'noclasses': True,  # no RSS
    }
}
