# Geometry Operation API

Operations always works with Geometry, not Feature.

Operation doc taken from [geodjango](https://docs.djangoproject.com/en/1.6/ref/contrib/gis/geos/).

[TOC]

## Stored Geometry Operations

Operations on stored feature's geometry.

### Unary

Operations on single geometry.

#### Endpoint

    GET /operations/:operation/:key

#### Operations

##### Unary Geometry Properties

Returns a POD result.

Operation | Parameters | Description
----------|------------|----------------------
type      |            | Type of the geometry
coords    |            | Returns the number of coordinates in the geometry. 
geoms     |            | Returns the number of geometries in this geometry. In other words, will return 1 on anything but geometry collections.
area      | `srid`     | Area of the geometry in `srid` unit
length    | `srid`     | Length of the geometry in `srid` unit
is_empty  |            | Returns whether or not the set of points in the geometry is empty.
is_simple |            | Returns a boolean indicating whether the geometry is simple. A geometry is simple if and only if it does not intersect itself (except at boundary points).


##### Unary Topological Properties

Returns a new geometry.

Operation        | Parameters       | Description
-----------------|------------------|--------------
boundary         | `format`, `srid` | Boundary of the geometry
centroid         | `format`, `srid` | Returns a Point object representing the geometric center of the geometry. The point is not guaranteed to be on the interior of the geometry.
convex_hull      | `format`, `srid` | Returns the smallest Polygon that contains all the points in the geometry.
envelope         | `format`, `srid` | Returns a Polygon that represents the bounding envelope of this geometry.
point_on_surface | `format`, `srid` | Computes and returns a Point guaranteed to be on the interior of this geometry.

##### Unary Topological Methods

Returns a new geometry.

Method           | Parameters                            | Description
-----------------|---------------------------------------|----------
buffer           | `width`, `quadsegs`, `format`, `srid` | Returns a geometry that represents all points whose distance from this geometry is less than or equal to the given width.
simplify         | `tolerance`, `topo`, `format`, `srid` | Returns a new geometry, simplified using the Douglas-Peucker algorithm to the specified tolerance

#### Parameters

Common Parameters:

Name      | Type    | Description
----------|---------|--------------------
`:operation`| string| Name of the operation
`:key`    | string  | Key of the geometry    
`format`  | string  | Format of the return geometry, one of `json`, `ewkt`, `ewkb`, default is `json`
`srid`    | integer | SRID of the geometry, default is `0`, geometry will be converted to `srid` before operation

`Buffer` Operation Parameters:

Name      | Type    | Description
----------|---------|--------------------
`width`   | float   | Width of the buffer
`quadsegs`| integer | keyword sets the number of segments used to approximate a quarter circle (defaults is 8).

`Simplify` Operation Parameters:

Name        | Type    | Description
------------|---------|--------------------
`tolerance` | float   | Tolerance of the simplification algorithm.  A higher tolerance value implies less points in the output.
`topo`      | boolean | By default, this function does not preserve topology. By setting this parameter to `true`, the result will have the same dimension and number of components as the input, however, this is significantly slower.


### Binary

Operations on two geometries.

#### Endpoint
    
    GET /operations/:operation/:this/:other

#### Operations

##### Binary Geometry Predicates

Returns POD result.

Operation   | Description
------------|-----------------
overlaps    | Returns True if the DE-9IM intersection matrix for the two geometries is `T*T***T**` (for two points or two surfaces) `1*T***T**` (for two curves). 
touches     | Returns True if the DE-9IM intersection matrix for the two geometries is `FT*******`, `F**T*****` or `F***T****`.
crosses     | Returns True if the DE-9IM intersection matrix for the two geometries is `T*F**F***`.
intersects  | Returns True if disjoint is False.
within      | Returns True if the DE-9IM intersection matrix for the two geometries is `T*F**F***`.
disjoint    | Returns True if the DE-9IM intersection matrix for the two geometries is `FF*FF****`.
contains    | Returns True if within is False.
equals      | Returns True if the DE-9IM intersection matrix for the two geometries is `T*F**FFF*`.

##### Binary Geometry Methods

Operation   | Description
------------|-----------------
distance    | Returns the distance between the closest points on this geometry and the other geometry

##### Binary Topological Methods

Returns a new geometry:

Operation    | Parameters       | Description
-------------|------------------|------------
intersection | `format`, `srid` | Returns a geometry representing the points shared by this geometry and other.
difference   | `format`, `srid` | Returns a geometry combining the points in this geometry not in other, and the points in other not in this geometry.
union        | `format`, `srid` | Returns a geometry representing all the points in this geometry and the other.


#### Parameters

Common Parameters:

Name         | Type    | Description
-------- ----|---------|--------------------
`:operation` | string  | Name of the operation
`:this`      | string  | Key of the geometry as first operation parameter
`:other`      | string  | Key of the geometry as second operation parameter
`format`  | string  | Format of the return geometry, one of `json`, `ewkt`, `ewkb`, default is `json`
`srid`    | integer | SRID of the geometry, default is `0`, geometry will be converted to `srid` before operation


## Posted Geometry Operation

Operations on geometries posted by API caller.

### Unary

#### Endpoint
    
    POST /operations/:operation

#### Request
    
Post a GeoJSON `Geometry` object:
    
    Data:
        <geojson geometry>
    Content-Type:
        application/json
        
### Binary

#### Endpoint
    
    POST /operations/:operation

#### Request
    
Post a GeoJSON `GeometryCollection` object which contains extract two geometries.  The first one is `this` geometry, the second one is `other` geometry:
    
    Data:
        <geojson geometry>
    Content-Type:
        application/json
        
### Mixed Binary    

    POST /geometries/:this/operation

#### Request
    
Post a GeoJSON `Geometry` object which is `other` geometry:
    
    Data:
        <geojson geometry>
    Content-Type:
        application/json
        

        