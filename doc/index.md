# GeoRest

Restful geospatial feature storage/query/operation interface.

> WARNING: API is subject to change until 1.0.0 release

[TOC]


## Spatial Data
    
### Geo Formats

All spatial data is exchanged using GeoJson.  
Besides GeoJson, `ewkt` and `ewkb` are also supported when getting or storing  geometries.

Note `ewkt`/`ewkb` does not support `GeometryCollection`.

By default, all feature's geometry are 2d and in epsg:4326 CRS.

### CRS

Coordinate Reference System (CRS), or Spatial Reference System (SRS) is an optional parameter of GeoJson standard.  If no CRS is specified, defualt CRS is `WGS84`, or `SRID4326`.  However, EWKT and EWKB supports arbitrary projections.

### Dimension

All features are 2D by default, as GeoJson does not support 3D geometries.

## Restful API

### Schema

All data is sent and received as JSON.  For geometries/features, GeoJson is used unless explicitly specified.

Request content type header is always:

    Content-Type: application/json
    
### Http Status Codes

Code  | Description
------|------------
200   | OK
201   | Stored
204   | No content
400   | Bad request, invalid request body or parameter
404   | Not found
409   | Conflict
500   | Internel server error

### Errors

Standard error response:

```json
{
    "code": 404,
    "message": "That thing is not found",
    "exception": "ThingNotFound"    
}
```

### Operation Result

```json
{
    "result": "blah"
}
```

### Response Headers 

General response headers when getting/setting a geometry/feature:

``` text
Content-Type: application/json
Etag: 3be55d5f844a2a4abf5efeb03d0b0e1ebcdc0a74
Date: Mon, 14 Apr 2014 07:35:00 GMT
Last-Modified: Mon, 14 Apr 2014 07:35:00 GMT
Cache-Control: max-age=30,must-revalidate
Expires:  Mon, 14 Apr 2014 07:35:30 GMT  
```    

### Http Verbs

Verb  | Description
------|------------
HEAD  | Can be issued against any resource to get just the HTTP header info.
GET   | Used for retrieving resources.
POST  | Used for creating resources, or performing custom actions.
PUT	  | Used for replacing resources or collections.
DELETE | Used for deleting resources.

## Endpoints

- [Geospatial Features](api_geo.md)  
- [Geometry Operations](api_ops.md)

