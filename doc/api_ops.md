# Geometry operation API

## Operations

### Unary

Unary Geometry Properties

Operation | Supported parameters | Description
--------- | ---------- | -----------

Unary Topological Properties

Operation | Supported parameters | Description
--------- | ---------- | -----------

Unary Topological Methods

Operation | Supported parameters | Description
--------- | ---------- | -----------

### Binary

### Variadic

## Request
```
GET /ops/:op/:key
GET /ops/:op/:key1/:key2
POST /ops/:op
```

Using `GET` method, operation parameters are sent as url query parameters.

`POST` content format:

```json
{
  "geometries": [],
  "parameters": {}
}
```

If geometry provided as string, geometry will be fetched from storage; if
provided as object, GeoJson geometry is assumed.
