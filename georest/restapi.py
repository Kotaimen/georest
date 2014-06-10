"""
    georest.api
    ~~~~~~~~~~~~

    Rest API hub
"""

from georest import view


class GeoRestApi(object):
    """The API hub of georest"""
    def __init__(self, app):
        self.app = app
        self.add_resources()

    def add_resource(self, resource, *urls, **kwargs):
        """utility method to add resources

        :param resource: flask view
        :param urls: url rules to apply
        :param kwargs: applied to app.add_url_rule as-is
        """
        for url_rule in urls:
            self.app.add_url_rule(url_rule, view_func=resource, **kwargs)

    def add_resources(self):
        """bind api urls to app"""
        self.add_resource(view.Describe.as_view('describe'), '/describe',
                          endpoint='describe')
