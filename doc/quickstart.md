# Quick Start

[TOC]

## Build & Installation

Check README for detail

## Configuration

Georest will try to read `settings.py` as settings file, default settings are
imported from `georest.default_settings`.

### Supported Configuration Values

name | description
---- | -----------
STORAGE | storage configuration
FEATURE_MODEL | feature model configuration

## Store some features
```shell
curl -X PUT http://localhost:5000/features/foo.bar\
     -H 'Content-Type: "application/json"'\
     -d '{"type":"Feature","geometry":{"type":"Point","coordinates":[30,10]},"properties":{}}'

curl -X PUT http://localhost:5000/features/foo.zoo\
     -H 'Content-Type: "application/json"'\
     -d '{"type":"Feature","geometry":{"type":"Point","coordinates":[20,20]},"properties":{}}'
```

## Do some geometry calculation
```shell
curl http://localhost:5000/operations/symmetric_difference/foo.bar/foo.zoo
```
