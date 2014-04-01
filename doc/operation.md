# Geometry Operation

Implements some of OGR Simple Geometry operations.

## Endpoints

Num     | Geometry | Method | Endpoint
--------|----------|--------|-----------
Unary   | Stored   | GET    | /geometries/`key`/`operation`?`param`=value
Binary  | Stored   | GET    | /geometries/`this`/`operation`/`other`?`param`=value
Unary   | Posted   | POST   | /operation/`operation`&`param`=value
Binary  | Posted   | POST   | /operation/`operation`&`param`=value
Binary  | Stored+Posted | POST | /geometries/`key`/`operation`?`param`=value

## Unary Geometry Properties

Property  | Parameters
----------|--------
type      | `srid`
coords    | `srid`
geoms     | 
area      | `srid`
length    | `srid`
is_empty  | 
is_simple | 

Returns simple POD:

``` json
{
    "result": false
}
```
### Parameters:

- `key`: Key of the geometry
- `srid`: Integer, SRID of the geometry, default is `0`, affects area/length operations

## Unary Topological Properties

Property         | Parameters
-----------------|-----------
boundary         | `format`, `srid`
centroid         | `format`, `srid`
convex_hull      | `format`, `srid`
envelope         | `format`, `srid`
point_on_surface | `format`, `srid`

Returns result geometry.

### Parameters:

- `key`: Key of the geometry
- `format`: Format of the return geometry, one of `json`, `ewkt`, `ewkb`, default is `json`
- `srid`: Integer, SRID of the geometry, default is 0

## Unary Topological Methods

Method           | Parameters
-----------------|-----------
buffer           | `width`, `quadsegs`, `format`, `srid`
simplify         | `tolerance`, `topo`, `format`, `srid`

Returns result geometry.

### Common Parameters

- `key`: Key of the geometry
- `format`: Format of the return geometry, one of `json`, `ewkt`, `ewkb`, default is `json`
- `srid`: Integer, SRID of the geometry, default is `0`

### `Buffer` Parameters
- `width`: float, width of the buffer
- `quadsegs`: integer, number of segments for 1/4 circle, default is `8`

### `Simplify` Parameters
- `tolerance`: 
- `topo`: Whether to preseve topological structure of the geometry, default is `false`

## Binary Geometry Predicates

Property         | Parameters
-----------------|------------
overlaps         | 
touches          |
crosses          |
intersects       |
within           |
disjoint         |
contains         |
equals           |

Returns simple POD:

``` json
{
    "result": false
}
```
