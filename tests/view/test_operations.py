# -*- encoding: utf-8 -*-

__author__ = 'pp'
__date__ = '6/25/14'


import json
import unittest

import mock

from georest import geo
from georest.model.operations import OperationResult
from tests.view.base import ViewTestMixin


class TestOperations(ViewTestMixin, unittest.TestCase):
    def setUp(self):
        super(TestOperations, self).setUp()
        self.geojsons = [
            '{"type":"Point","coordinates":[30,10]}',
            '{"type":"Polygon","coordinates":[[[30,10],[40,40],[20,40],[10,20],[30,10]]]}',
            '{"type":"MultiPoint","coordinates":[[10,40],[40,30],[20,20],[30,10]]}',
            '{"type":"MultiPolygon","coordinates":[[[[30,20],[45,40],[10,40],[30,20]]],[[[15,5],[40,10],[10,20],[5,10],[15,5]]]]}',
        ]

    def test_get_unary(self):
        self.mock_operations_model.invoke.return_value = OperationResult(100, True)
        geom = geo.Geometry.build_geometry(self.geojsons[0])
        self.mock_geometry_model.get.return_value = geom, {}
        r = self.client.get('/operations/kangaroo/foo.bar?srid=1050&owl=Tyto')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(json.loads(r.data), {'result': 100})
        self.mock_operations_model.invoke.assert_called_once_with('kangaroo', geom, srid=1050, owl='Tyto')
        self.mock_geometry_model.get.assert_called_once_with('foo.bar')

    def test_get_binary(self):
        result_geom = geo.Geometry.build_geometry(self.geojsons[1])
        self.mock_operations_model.invoke.return_value = OperationResult(result_geom, False)
        geom1 = geo.Geometry.build_geometry(self.geojsons[2])
        geom2 = geo.Geometry.build_geometry(self.geojsons[3])
        self.mock_geometry_model.get.side_effect = [(geom1, {}), (geom2, {})]
        r = self.client.get('/operations/hedgehog/knit.net/bit.bot?cat=Mike')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(json.loads(r.data), json.loads(self.geojsons[1]))
        self.mock_operations_model.invoke.assert_called_once_with('hedgehog', geom1, geom2, cat='Mike')
        self.mock_geometry_model.get.assert_has_calls(
                         map(mock.call, ['knit.net', 'bit.bot']))

    def test_get_literal_fail(self):
        r = self.client.get('/operations/hedgehog/~?cat=Mike')
        self.assertEqual(r.status_code, 400)
        r = self.client.get('/operations/hedgehog/~.1?cat=Mike')
        self.assertEqual(r.status_code, 400)

    def test_post_unary(self):
        self.mock_operations_model.invoke.return_value = OperationResult(100, True)
        r = self.client.post('/operations/kangaroo/~?srid=1050&owl=Tyto',
                             content_type='application/json',
                             data=self.geojsons[0])
        self.assertEqual(r.status_code, 200)
        self.assertEqual(json.loads(r.data), {'result': 100})
        call, = self.mock_operations_model.invoke.call_args_list
        #('kangaroo', geom, srid=1050, owl='Tyto')
        args, kwargs = call
        op_name, geom = args
        self.assertEqual(op_name, 'kangaroo')
        self.assert_(geom.equals(geo.Geometry.build_geometry(self.geojsons[0])))
        # self.mock_geometry_model.get.assert_called_once_with('foo.bar')
        self.assertEqual(kwargs, {'srid': 1050, 'owl': 'Tyto'})

    def test_post_vari(self):
        self.mock_operations_model.invoke.return_value = OperationResult(100, True)
        result_geom = geo.Geometry.build_geometry(self.geojsons[0])
        geom = geo.Geometry.build_geometry(self.geojsons[1])
        self.mock_operations_model.invoke.return_value = OperationResult(result_geom, False)
        self.mock_geometry_model.get.return_value = geom, {}
        r = self.client.post('/operations/kangaroo/~.0/knit.net/~.1?cat=Mike',
                             content_type='application/json',
                             data=self.geojsons[3])
        self.assertEqual(r.status_code, 200)
        self.assertEqual(json.loads(r.data), json.loads(self.geojsons[0]))
        self.mock_geometry_model.get.assert_called_once_with('knit.net')

    def test_post_fail(self):
        r = self.client.post('/operations/kangaroo/~.0/~.10?cat=Mike',
                             content_type='application/json',
                             data=self.geojsons[3])
        self.assertEqual(r.status_code, 400)

        r = self.client.post('/operations/kangaroo/~.0/~.10?cat=Mike',
                             content_type='application/json',
                             data=self.geojsons[0])
        self.assertEqual(r.status_code, 400)

        r = self.client.post('/operations/kangaroo/~?srid=bad',
                             content_type='application/json',
                             data=self.geojsons[0])
        self.assertEqual(r.status_code, 400)

        r = self.client.post('/operations/kangaroo/~.bad',
                             content_type='application/json',
                             data=self.geojsons[0])
        self.assertEqual(r.status_code, 400)


class TestAttributes(ViewTestMixin, unittest.TestCase):
    def test_attributes(self):
        jdata = '{"foo": "bar"}'
        geom = geo.Geometry.build_geometry('{"type":"Point","coordinates":[30,10]}')
        self.mock_attributes_model.attributes.return_value = jdata
        self.mock_geometry_model.get.return_value = geom, {}
        r = self.client.get('/features/kanga.roo/geometry/attributes',
                            query_string={'srid': '100',
                                          'include_length': 'T',
                                          'exclude_area': 'T',
                                          'foo': 'bar'})
        self.assertEqual(r.status_code, 200)
        self.mock_geometry_model.get.assert_called_once_with('kanga.roo')
        self.mock_attributes_model.attributes.assert_called_once_with(geom,
                                                                      includes=['length'],
                                                                      excludes=['area'],
                                                                      srid=100,
                                                                      foo='bar')
