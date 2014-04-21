# Geospatial Resource API

[TOC]

## Data Model

Georest implements a schema-less data model:

    Collection
      |-Features{}
          |-Geometry
          |   |-SRID
          |-Properties{}
              |- (Name, Value)          


## Key

Each feature has a unique `key` which must match following regular expression:

    [a-z][a-zA-Z0-9_-]+

These keys are reserved:

    geometry
    properties

## Namespace

> Not implemented.

## Geometries

Access geometry part of a feature object.  

### Create a New Geometry

Create a new feature with given geometry, with empty properties.  

#### Endpoints

    POST /features/geometry
    PUT /features/:key/geometry

`POST` create a new feature with a random unique `key` with optional `prefix`.

`PUT` will create a new feature if it does not exist, otherwise it replaces the existing geometry.

#### Parameters

Name      | Type    | Description
----------|---------|--------------------
`:key`    | string  | Key of the new geometry.
`prefix`  | string  | Optional string prepend to key when creating a new geometry.  If `:key` not is provided, default value is `feature.`.

#### Request

    Data: 
        <geometry>
    Headers:
        Content-type: application/json            

`geometry` can be one of following format:

    geojson geometry
    wkt
    ewkt
    hexwkb
    hexewkb

Allowed geometry types: 
    
    Point
    Linestring
    Polygon
    MultiPoint
    MultiLinestring
    MultiPolygon
    GeometryCollection

Note empty or invalid geometry is not allowed.
`GeoJson/WKT/WKB` default SRID=4326.

#### Response

Status:
    
    201 Created
    
Data:

```json
{
    "code": 201,
    "key": "<key_of_created_feature>"
}
```

### Retrieve a Geometry

Retrieve geometry object of given feature with specified format and SRID.

#### Endpoint

    GET /features/:key/geometry

#### Parameters
    
Name      | Type    | Description
----------|---------|--------------------
`:key`    | string  | Key of the geometry
`format`  | string  | Format of the return geometry, one of `json`, `ewkt`, `ewkb`.  Default is `json`
`srid`    | integer | SRID of the geometry, default is `0` (which means "as is")
`prefix`  | string  | Optional string to prepend to key

#### Response

Returns requested geometry.  Content type depends on requested format:

Format    | Content Type
----------|---------------
`json`    | `application/json`
`ewkt`    | `text/plain`
`exkb`    | `application/oct-stream`


## Features

### Create a New Feature

#### Endpoints

`POST` will create a new feature with a random unique `key` with optional `prefix`, PUT will create new feature if it does not exist.

    POST /features
    PUT /features/:key

#### Parameters

Name      | Type    | Description
----------|---------|--------------------
`:key`    | string  | Key of the new feature.
`prefix`  | string  | Optional string to prepend to key when creating a new feature.  If `:key` not is provided, default value is `feature-`.

#### Request

Feature data must be a GeoJson `Feature` object.

    Data: 
        <GeoJson Feature>
    Headers:
        Content-type: application/json            

#### Response
    
    Status: 201 Created
    
    {
        "code": 201,
        "key": "<key_of_created_feature>"
    }


### Retrieve a Feature

#### Endpoint
    
    GET /features/:key

#### Parameters

Name      | Type    | Description
----------|---------|--------------------
`:key`    | string  | Key of the geometry    
`prefix`  | string  | Optional string to prepend to key
    
#### Response

``` json
{
    "type": "Feature", 
    "geometry": {
        "type": "Point", 
        "coordinates": [
            0.0001, 
            0.0001
        ]
    }, 
    "properties": {
        "name": "feature1"
    }, 
    "crs": {
        "type": "name", 
        "properties": {
            "name": "EPSG:4326"
        }
    },     
    "bbox": [
        0.0001, 
        0.0001, 
        0.0001, 
        0.0001
    ],     
    "_geohash": "s0000000d6ds", 
    "_modified": "Mon, 14 Apr 2014 07:35:00 GMT", 
    "_created": "Mon, 14 Apr 2014 07:35:00 GMT", 
    "_key": "point1", 
    "_etag": "3be55d5f844a2a4abf5efeb03d0b0e1ebcdc0a74"
}  
```

    
### Delete a Feature

#### Endpoint
        
    DELETE /features/:key

#### Parameters

Name      | Type    | Description
----------|---------|--------------------
`:key`    | string  | Key of the feature    
`prefix`  | string  | Optional string to prepend to key

#### Response
    
    Code: 204

### Feature Attributes

Access special feature attributes.

#### Geohash

Get `geohash` of the feature as a string with precision is 12:

    GET /features/:key/geohash
    
Response:

```json
{
    "result": "s012345"
}
```    
#### Envelope

Get envelope (bounding box) of the feature as a point list:   

    GET /features/:key/bbox

Response:

```json
{
    "result": [
        1.0, 
        1.0, 
        2.0, 
        2.0
    ]
}
```
    
## Properties

Access properties part of a feature object.

> Not implemented yet.

### Update Properties

Update properties dictionary.


    POST /features/:key/properties

Request:

    Data:
        <properties>
    Content-Type:
        application/json

`properties` must be a JSON dictionary.

Response:

    201 Created
    
Return updated properties.

### Retrieve All Properties

Endpoint:
    
    GET /features/:key/properties

Response:
    
    200 OK
    Data: Properties
    
### Delete All Properties

Endpoint:

    DELETE /features/:key/properties

Response:
    
    204 No Data

### Retrieve a Property by Name

> Not implemented

Endpoint:
        
    GET /features/:key/properties/:name

### Replace a Property by Name 

> Not implemented

Endpoint:

    PUT /features/:key/properties/:name    
    
### Delete a Property by Name

> Not implemented

Endpoint:
    
    DELETE /features/:key/properties/:name   
    
