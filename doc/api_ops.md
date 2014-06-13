# Geometry operation API

## Operations

### Unary

Unary Geometry Properties

Operation | Parameters | result    | Description
--------- | ---------- | --------- | -----------
area      | `srid`     | pod/float | Area of the geometry in `srid` unit

Unary Topological Properties

Operation | Parameters | result    | Description
--------- | ---------- | --------- | -----------
boundary  | `srid`     | geojson   | Boundary of the geometry

Unary Topological Methods

Operation | Parameters                  | result    | Description
--------- | --------------------------- | --------- | -----------
buffer    | `width`, `quadsegs`, `srid` | geojson   | Returns a geometry that represents all points whose distance from this geometry is less than or equal to the given width.


### Binary

Binary Geometry Predicates

Operation | result    | Description
--------- | --------- | -----------
overlaps  | pod/bool  | Returns True if the DE-9IM intersection matrix for the two geometries is `T*T***T**` (for two points or two surfaces) `1*T***T**` (for two curves).

Binary Geometry Methods

Operation | result     | Description
--------- | ---------- | -----------
distance  | pod/float  | Returns the distance between the closest points on this geometry and the other geometry

Binary Topological Methods

Operation    | Parameters | result    | Description
------------ | ---------- | --------- | -----------
intersection | `srid`     | geojson   | Returns a geometry representing the points shared by this geometry and other.


### Variadic

Operation | Parameters | result    | Description
--------- | ---------- | --------- | -----------
union     | `srid`     | geojson   | Returns a geometry representing all the points in all given geometries.

## Query parameters

## Request

### URL pattern

```
/ops/:op/:key  # for unary operations
/ops/:op/:key1/:key2  # for binary operations
/ops/:op/:keys-split-by-slash  # for variadic operations
```

### GET method

When using `GET` method, all geometry-keys **MUST** exist.

For example:

```
GET /ops/overlaps/foo.bar/hodor.hodor
```

### POST method

When using `POST` method:

  - the posted content **MUST** be an geojson geometry.
  - `~` can be used as a key, to represent the posted geometry.
  - `~.<i>` can also be used as a key, When posted geometry is a 
    multi-geometry(e.g. geometry collection), to represent the `<i>`th
    sub-geometry in the posted geometry, start from **0**.

For example:

```
POST /ops/overlaps/~/hodor.hodor

-d
{
  "type": "Point",
  "coordinates": [100, 105]
}
```

```
POST /ops/overlaps/~.0/~.1

-d
{
  "type": "GeometryCollection",
  "geometries": [
    {
      "type": "Point",
      "coordinates": [100, 105]
    },
    {
      "type": "Polygon",
      "coordinates": [
        [100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0]
      ]
    }
  ]
}
```

## Response

When result type is geojson, a success operation response is **ALWAYS** geojson
document, representing the resulted geometry.
