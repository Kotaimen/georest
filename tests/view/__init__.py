# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '3/23/14'

import datetime
import json
import uuid

from georest import GeoRestApp
from georest.geo import build_feature


class ResourceTestBase(object):
    def setUp(self):
        # Build test features

        # Round timestamp since http header timestamp has 1 second resolution
        timestamp = datetime.datetime.utcnow().replace(microsecond=0)

        self.point1 = build_feature('POINT (0.0001 0.0001)',
                                      {'question': 'meaning of life',
                                       'answer': 42},
                                      srid=4326,
                                      key=uuid.uuid4(),
                                      created=timestamp)

        # Reset modified timestamp since build_feature recalculates it
        self.point1._modified = timestamp

        self.linestring1 = build_feature(
            'LINESTRING (0.00015 -0.00015, 0.00016 -0.00017)', )

        feature3 = build_feature(
            'POLYGON ((0 0, 1 0, 1 1, 0.5 1, 0.5 0.5, 0 0.5, 0 0))'
        )

        # Load test settings
        settings = {
            'GEOREST_GEOSTORE_CONFIG': {'type': 'memory'},
            'GEOREST_GEOMODEL_CONFIG': {'type': 'simple'},
        }

        # Create test app
        self.app = GeoRestApp(settings=settings)
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

        # Preload test features into store
        self.app.model.store.put_feature(self.point1, 'point1')
        self.app.model.store.put_feature(self.linestring1, 'linestring1')
        self.app.model.store.put_feature(feature3, 'polygon1')

    def tearDown(self):
        pass

    def checkResponse(self, response, status_code=200):
        self.assertEqual(status_code, response.status_code)
        self.assertEqual('application/json', response.content_type)
        if status_code == 204:  # No content
            return None
        else:
            data = json.loads(response.data)
            return data
