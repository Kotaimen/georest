# Feature persistence API

## Concepts, Data structure and conventions

### Feature

Georest feature is a schema-less,
[Geojson](http://geojson.org/geojson-spec.html) Feature compatible geographic
feature structure, with a few restrictions and conventions:

  - Geometry Collection geometry object is not allowed as input.
  - Feature with null geometry object is not allowed as input.
  - "id" of Feature will be ignored even if provided.
  - Only named CRS allowed. For now, only ESPG codes allowed in named CRS.
  - "properties" of Feature must be a json object, null is not allowed.
  - only 2-dim geometries allowed for now.

### Key

Key is global identifier of persisted features. It is a string with words
and dots.

```
bucket := <[A-Za-z][A-Za-z0-9_]+>
name := <([A-Za-z0-9_]+\.)*[A-Za-z0-9_]+>
key := bucket.name
```

## Store feature

### Request
```
POST /features
PUT /features/:key
```

Using POST, Georest will assign a key under given namespace.

Optional headers:

  - If-None-Match, If-Match, If-Modified-Since, and If-Unmodified-Since
    invoke conditional request semantics, matching on the ETag and
    Last-Modified of the existing object.

Optional query parameters:

  - `namespace` - feature's key is created under this namespace when using POST
                  (default to null)

### Response

Normal response codes:

  - `200 OK`
  - `201 Created`

Typical error codes:

  - `400 Bad Request` - e.g. invalid request data/format
  - `409 Conflict` if one of the conditional request headers failed
                              to match (see above)

Success response body:

```json
{
  "code": <status_code>,
  "key": "<key>",
}
```

## Fetch Feature
```
GET /features/:key
```

Normal response codes:

  - `200 OK`
  - `404 Not Found`

## Delete Feature
```
DELETE /features/:key
```

Normal response codes:

  - `204 No Content`
  - `404 Not Found`
  - `409 Conflict` if one of the conditional request headers failed
                              to match (see above)

## Store Geometry
```
PUT /features/:key/geometry
```
Updates geometry if given `:key` exists. Create feature if key does not exist.
If automatic naming is required, use Feature resource instead. Although
Geometry cannot be deleted, use delete feature instead.

Normal response codes:

  - `200 OK`
  - `201 Created`

Typical error codes:

  - `400 Bad Request` - e.g. invalid request data/format
  - `409 Conflict` if one of the conditional request headers failed
                              to match (see above)



## Fetch Geometry
```
GET /features/:key/geometry
```

Normal response codes:

  - `200 OK`
  - `404 Not Found`

## Update Properties
```
PUT /features/:key/properties
```
Normal response codes:

  - `200 OK`
  - `404 Not Found`

Typical error codes:

  - `400 Bad Request` - e.g. invalid request data/format
  - `409 Conflict` if one of the conditional request headers failed
                              to match (see above)

> There is no PATCH support for now. consider use
[RFC 6902](http://tools.ietf.org/html/rfc6902) if it's needed


## Fetch Properties
```
GET /features/:key/properties
```

Normal response codes:

  - `200 OK`
  - `404 Not Found`

