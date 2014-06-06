# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '6/1/14'

""" Various geo library performance benchmark

NaturalEarth 10m_cultural data from http://www.naturalearthdata.com.
"""

import time
import os
import glob
import itertools
import functools
import io
import gc

import geojson
import geojson.mapping
import json
import simplejson
import ujson
import yajl

import shapefile
from osgeo import ogr
import shapely.geometry
import shapely.wkb
import shapely.wkt
import shapely.speedups

shapely.speedups.enable()

#
# Simple Feature object
#
class Feature(object):
    def __init__(self, geometry, properties):
        self.geometry = geometry
        self.properties = properties

    @property
    def __geo_interface__(self):
        return dict(type='Feature',
                    geometry=shapely.geometry.mapping(self.geometry),
                    properties=self.properties)


#
# Geometry builders
#
def dummy_geometry_builder(obj):
    return obj


def shapely_geometry_builder(obj, copy=True):
    if copy:
        return shapely.geometry.shape(obj)
    else:
        return shapely.geometry.asShape(obj)


def shapely_wkb_geometry_builder(obj):
    return shapely.wkb.loads(obj.ExportToWkb())


#
# Shapefile readers
#
def read_shapefile_using_pyshp(filename, builder=dummy_geometry_builder):
    reader = shapefile.Reader(filename)
    prop_keys = list(f[0] for f in reader.fields[1:])

    for shape in reader.shapeRecords():
        properties = dict(itertools.izip(prop_keys, shape.record))
        geometry = builder(shape.shape)
        feature = Feature(geometry, properties)
        yield feature


def read_shapefile_using_ogr(filename, builder=dummy_geometry_builder):
    data_source = ogr.Open(filename)
    layer_count = data_source.GetLayerCount()

    def unicode(s):
        return s.decode('iso8859-1') if isinstance(s, str) else s

    for layer_index in range(layer_count):
        layer = data_source.GetLayerByIndex(layer_index)
        # layer_name = layer.GetName()

        while True:
            feature = layer.GetNextFeature()
            if feature is None:
                break
            geometry = builder(feature.GetGeometryRef())
            properties = dict(
                ((k, unicode(feature.GetField(k))) for k in feature.keys()))

            feature_object = Feature(geometry, properties)
            yield feature_object


#
# Shapefile benchmarks
#

def benchmark_shapefile_read(filenames, reader):
    features = list()
    errors = 0

    tic = time.clock()
    for filename in filenames:
        try:
            features.extend(reader(filename))
        except Exception as e:
            # raise
            errors += 1
    tac = time.clock() - tic
    print '%d files, %d features in %f seconds, %d errors.' % (len(filenames),
                                                               len(features),
                                                               tac, errors)
    return features


#
# Json
#

def benchmark_geojson_dump(features, writer=geojson.dump):
    buf = io.BytesIO()
    tic = time.clock()

    for feature in features:
        writer(geojson.mapping.to_mapping(feature), buf)
        buf.write('\n')

    tac = time.clock() - tic

    print '%d features, %d bytes in %f seconds.' % \
          (len(features), buf.tell(), tac)

    return buf.getvalue()


def benchmark_geojson_load(data, builder=shapely_geometry_builder):
    features = list()
    tic = time.clock()
    for line in data.splitlines():
        geojson_feature = geojson.loads(line)
        feature = Feature(builder(geojson_feature.geometry),
                          geojson_feature.properties)
        features.append(feature)

    tac = time.clock() - tic
    print '%d features in %f seconds.' % (len(features), tac)

    return features


def benchmark_ujson_load(data):
    features = list()
    tic = time.clock()
    for line in data.splitlines():
        python_feature = ujson.loads(line)
        geojson_feature = geojson.GeoJSON.to_instance(python_feature)
        feature = Feature(
            shapely_geometry_builder(geojson_feature.geometry, copy=False),
            geojson_feature.properties)
        features.append(feature)
    tac = time.clock() - tic
    print '%d features in %f seconds.' % (len(features), tac)

    return features


#
# Benchmark
#

def main():
    gc.disable()

    root = os.path.expanduser(
        r'~/proj/geodata/Vanilla/NaturalEarth3/10m_cultural/10m_cultural/ne_10m_admin_0*.shp')
    print root
    filenames = glob.glob(root)[:]

    #
    # Shapefile read
    #
    print 'Read shapefile using osgeo.ogr...',
    benchmark_shapefile_read(filenames, read_shapefile_using_ogr)

    # NOTE: pyshp is so slow and can't read some NaturalEarth files...
    print 'Read shapefile using pyshp...',
    benchmark_shapefile_read(filenames, read_shapefile_using_pyshp)

    print 'Build Features from shapefile...',
    all_features = benchmark_shapefile_read(filenames,
                                            functools.partial(
                                                read_shapefile_using_ogr,
                                                builder=shapely_wkb_geometry_builder))

    #
    # Json Dump
    #
    print 'Dump as GeoJson using geojson (via simplejson)...',
    data = benchmark_geojson_dump(all_features, writer=geojson.dump)
    # with open('geojson.txt', 'wb') as fp: fp.write(data)

    print 'Dump as GeoJson using ujson...',
    data = benchmark_geojson_dump(all_features, writer=ujson.dump)

    # NOTE: yajl crashes when writing to a stream, slower than ujson anyway
    # print 'Dump as GeoJson using yajl...',
    # data = benchmark_geojson_dump(all_features, writer=yajl.dump)


    #
    # Json Load
    #
    print 'Build Features from geojson (via simplejson)...',
    benchmark_geojson_load(data)
    print "Build Features from geojson (don't copy geometry)...",
    benchmark_geojson_load(data,
                           builder=functools.partial(shapely_geometry_builder,
                                                     copy=False))
    print 'Build Features from geojson using ujson ...',
    benchmark_ujson_load(data)


if __name__ == '__main__':
    main()