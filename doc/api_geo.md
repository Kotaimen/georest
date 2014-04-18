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

Allowed geometry types: 
    
    Point
    Linestring
    Polygon
    MultiPoint
    MultiLinestring
    MultiPolygon
    GeometryCollection

Note empty or invalid geometry is not allowed.

#### Endpoints

    POST /features/geometry
    PUT /features/:key/geometry

`POST` will create a new feature with a random unique `key` with optional `prefix`, `PUT` will create new feature if it does not exist, otherwise replaces the existing one.

#### Parameters

Name      | Type    | Description
----------|---------|--------------------
`:key`    | string  | Key of the new geometry.
`prefix`  | string  | Optional string to prepend to key when creating a new geometry.  If `:key` not is provided, default value is `feature.`.

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
`prefix`  | string  | Optional string to prepend to key when creating a new feature.  If `:key` not is provied, default value is `feature-`.

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

#### Response
    
    Code: 204

### Feature Attributes

Access special feature attributes.

#### Geohash

Get `geohash` of the feature as a string:

    GET /features/:key/geohash
    
#### BBOX

Get bounding box (envelope) of the feature as a point list:   

    GET /features/:key/bbox    

    
## Properties

Access properties part of a feature object.

> Not implemented yet.

### Update Properties

Update properties dictionary (existing properties got replaced).

#### Endpoint

    POST /features/:key/properties

#### Request

    Data:
        <properties>
    Content-Type:
        application/json

`properties` must be a json dictionary.

#### Response

    201 Created    
    
### Get Properties

#### Endpoint
    
    GET /features/:key/properties
    
### Delete All Properties

#### Endpoint

    DELETE /features/:key/properties

### Get a Property

#### Endpoint
        
    GET /features/:key/properties/:name

### Replace a Property    

#### Endpoint

    PUT /features/:key/properties/:name    
    
### Delete a Property

#### Endpoint
    
    DELETE /features/:key/properties/:name   
    
