# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '5/31/14'

import json

pydata = dict(
    point={"type": "Point", "coordinates": [100.0, 0.0]},
    linestring={"type": "LineString",
                "coordinates": [
                    [100.0, 0.0], [101.0, 1.0],
                ]
    },
    polygon={"type": "Polygon",
             "coordinates": [
                 [[100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0],
                  [100.0, 0.0]],
                 [[100.2, 0.2], [100.8, 0.2], [100.8, 0.8], [100.2, 0.8],
                  [100.2, 0.2]]
             ]
    },
    multipoint={"type": "MultiPoint",
                "coordinates": [[100.0, 0.0], [101.0, 1.0]]
    },
    multilinestring={"type": "MultiLineString",
                     "coordinates": [
                         [[100.0, 0.0], [101.0, 1.0]],
                         [[102.0, 2.0], [103.0, 3.0]]
                     ]
    },
    multipolygon={"type": "MultiPolygon",
                  "coordinates": [
                      [[[102.0, 2.0], [103.0, 2.0], [103.0, 3.0], [102.0, 3.0],
                        [102.0, 2.0]]],
                      [[[100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0],
                        [100.0, 0.0]],
                       [[100.2, 0.2], [100.8, 0.2], [100.8, 0.8], [100.2, 0.8],
                        [100.2, 0.2]]]
                  ]
    },
    geometrycollection={"type": "GeometryCollection",
                        "geometries": [
                            {"type": "Point",
                             "coordinates": [100.0, 0.0]
                            },
                            {"type": "LineString",
                             "coordinates": [[101.0, 0.0], [102.0, 1.0]]
                            }
                        ]
    }

)

jsondata = dict((k, json.dumps(v)) for k, v in pydata.iteritems())

