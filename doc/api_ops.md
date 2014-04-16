# Geometry Operation API

Operations always works with Geometry, not Feature.

[TOC]

## Operations on Stored Geometry

### Unary

#### Endpoint

    GET /operations/:operation/:key

#### Unary Geometry Properties

Returns a POD result.

Operation | Parameters | Description
----------|------------|----------------------
type      |            | Type of the geometry
coords    |            | Number of coordinates 
geoms     |            | Number of geometries
area      | `srid`     | Area of the geometry
length    | `srid`     | Length of the geometry
is_empty  |            | Whether geometry is empty
is_simple |            | Whether geometry is simple

#### Unary Topological Properties

Returns a new geometry.

Operation        | Parameters       | Description
-----------------|------------------|--------------
boundary         | `format`, `srid` | Boundary of the geometry
centroid         | `format`, `srid` | Centroid of the geometry
convex_hull      | `format`, `srid` | Convex hull of the geometry
envelope         | `format`, `srid` | Envelope of the geometry
point_on_surface | `format`, `srid` | A point on geometry surface

#### Unary Topological Methods

Returns a new geometry.

Method           | Parameters                            
-----------------|---------------------------------------
buffer           | `width`, `quadsegs`, `format`, `srid` 
simplify         | `tolerance`, `topo`, `format`, `srid` 

#### Parameters

Common Parameters:

Name      | Type    | Description
----------|---------|--------------------
`:key`    | string  | Key of the geometry    
`format`  | string  | Format of the return geometry, one of `json`, `ewkt`, `ewkb`, default is `json`
`srid`    | integer | SRID of the geometry, default is `0`, geometry will be converted to `srid` before operation

`Buffer` Parameters:

Name      | Type    | Description
----------|---------|--------------------
`width`   | float   | Width of the buffer
`quadsegs`| integer | Number of segments for 1/4 circle, default is `8`

`Simplify` Parameters:

Name        | Type    | Description
------------|---------|--------------------
`tolerance` | float   | Tolerance of the simplification
`topo`      | boolean |  Whether to preseve topological structure of the geometry, default is `false`

### Binary

#### Endpoint:

    
    GET /operations/:operation/:this/:other
    

#### Binary Geometry Predicates

Returns result.

Operation     | Description
--------------|-----------------
overlaps    | 
touches     |
crosses     |
intersects  |
within      |
disjoint    |
contains    |
equals      |

#### Binary Topological Methods

Returns a new geometry:

Operation      | Parameters       | Description
---------------|------------------|------------
intersection | `format`, `srid` |
difference   | `format`, `srid` |
union        | `format`, `srid` |

## Operations on Stored Geometry

#### Endpoint:
    
    POST /operations/:operation
    

#### Request:

- For unary operation, post a Geometry 
- For binary operation, post a GeometryCollection containing two geometries
    