# Geometry Resource

Access the Geometry object of a Feature.


## Error Handling

``` json
{
    "code": 404,
    "message": "Geometry not found: blah",
    "exception": "GeometryNotFound"
}
```

## Geometry Access
 

Action                | Method | Endpoint
----------------------|--------|------------------------
Create new geometry   | POST   | /geometries
Put geometry with key | PUT    | /geometries/`key`
Get geometry          | GET    | /geometries/`key`?`format`=json&`srid`=0
Delete geometry       | DELETE | /geometries/`key`

### Parameters

- `key`: Key of the geometry, must match regular expression `[a-z][a-zA-Z0-9_-]+`
- `format`: Format of the return geometry, one of 
    - `json`: GeoJSON geometry, default
    - `ewkt`: well known text with embedded SRID
    - `ewkb`: well known binary with embedded SRID
- `srid`: Integer, SRID of the geometry, default is 0, which means "don't change"

### Request Headers

```
Content-Type: "application/json"
```

### Request Body
Accepted format:
- GeoJson Geometry
- WKT/EWKT

Accepted geometry types:
- Point
- LineString
- Polygon
- MultiLineString
- MultiPolygon
- GeometryCollection


### Response

#### Create/Put

Returns `201` status code if successful, along with following data:

```json
{
    "code": 201,
    "key": "geometry-1"
}
```

> TODO...

#### Delete

Returns `200` status code if successful.

> TODO...

#### Get

Returns requested gometry according to requested format and srid.

> TODO...


## Example

> TODO...
