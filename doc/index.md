# GeoRest

Restful geospatial feature storage/query/operation interface.

## Data Model

Implements a schemaless data model:

    Collection
      |-Features{}
          |-Geometry
          |   |-SRID
          |-Properties{}
              |- (Key, Value)          

## API

- [Geometry Access](geometry.md)  
- [Geometry Operation](operation.md)
