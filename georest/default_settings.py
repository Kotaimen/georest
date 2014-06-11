# -*- encoding: utf-8 -*-

"""
    Default settings
"""

#
# Georest
#


#
# Flask-Markdown Plugin
#
MARKDOWN_EXTENSIONS = ['extra', 'toc', 'codehilite', ]

MARKDOWN_EXTENSION_CONFIGS = {
    'codehilite': {'pygments_style': 'autumn',
                   # for list of styles, run: pygmentize -L styles
                   'linenums': None,  # True=always, False=never, None=auto
                   'noclasses': True,  # no CSS generated
    }
}
