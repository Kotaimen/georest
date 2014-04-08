# Gepspatial Resource API

[TOC]

## Data Model

Georest implements a schemaless data model:

    Collection
      |-Features{}
          |-Geometry
          |   |-SRID
          |-Properties{}
              |- (Name, Value)          


## Key

Each feature has a unique `key`.

Key must match regular expression:

    [a-z][a-zA-Z0-9_-]+

Following keys are reserved:

    geometry
    properties

## Namespace

> Not implemented.

## Features

Get or store GeoJson Features object:

    POST /features
    GET /features/:key
    PUT /features/:key

> Only `GET /features/:key` is implemented.


### Get Feature Attributes

    GET /features/:key/geohash
    GET /features/:key/bbox    

## Geometries

Get or store Geometry of the Feature object:

### Create a Geometry

Endpoints:

    POST /features/geometry
    PUT /features/:key/geometry

Request:

    Data: geojson, wkt, ewkt, hexwkb, hexewkb
    Headers:
        Content-type: application/json            

Response:
    
    Status: 201 Created
    
    {
        "code": 201,
        "key": "<key_of_created_geometry>"
    }

### Retrieve a Geometry

Endpoint:

    GET /features/:key/geometry

Parameters:
    
Name      | Type    | Description
----------|---------|--------------------
`:key`    | string  | Key of the geometry
`format`  | string  | Format of the return geometry, one of `json`, `ewkt`, `ewkb`.  Default is `json`
`srid`    | integer | SRID of the geometry, default is 0 (which means "as is")
    
### Delete a Geometry

Delete the feature together with the geometry.

Endpoint:
        
    DELETE /features/:key/geometry

Parameters:

Name      | Type    | Description
----------|---------|--------------------
`:key`    | string  | Key of the geometry    

Response:
    
    Code: 204
    
## Properties

    POST /features/:key/properties
    GET /features/:key/properties
    GET /features/:key/properties/:name
    
> Not implemented.

