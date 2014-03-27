# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '3/23/14'

import datetime
import json

from georest import GeoRestApp
from georest.geo import build_feature


class ResourceTestBase(object):
    def setUp(self):
        # Build test features

        # Round timestamp since http header timestamp has 1 second resolution
        timestamp = datetime.datetime.utcnow().replace(microsecond=0)

        self.feature1 = build_feature('POINT (0.0001 0.0001)',
                                      {'name': 'feature1'},
                                      srid=4326,
                                      id_=1,
                                      created=timestamp)

        # Reset modified timestamp since build_feature recalculates it
        self.feature1._modified = timestamp

        self.feature2 = build_feature(
            'LINESTRING (0.00015 -0.00015, 0.00016 -0.00017)',
            {'name': 'feature2'})

        self.feature3 = build_feature(
            'POLYGON ((0 0, 1 0, 1 1, 0 1, 0 0))'
        )

        # Load test settings
        settings = {
            'GEOREST_GEOSTORE_CONFIG': {'type': 'simple'},
            'GEOREST_GEOMODEL_CONFIG': {'type': 'simple'},
        }

        # Create test app
        self.app = GeoRestApp(settings=settings)
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

        # Preload test features into store
        self.app.model.store.put_feature(self.feature1, 'point1')
        self.app.model.store.put_feature(self.feature2, 'linestring1')
        self.app.model.store.put_feature(self.feature3, 'polygon1')

    def tearDown(self):
        pass

    def checkResponse(self, response, status_code=200):
        self.assertEqual(status_code, response.status_code)
        self.assertEqual('application/json', response.content_type)
        data = json.loads(response.data)
        return data
