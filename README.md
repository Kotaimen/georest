# GeoRest

A restful, schema-less, searchable GeoFeature object storage.

## Features

- Restful API
- GeoJSON exchange format
- Geometry operation
- Spatial query
- Switchable storage backend
- Entity tracking support

## Install on Ubuntu 12.04

```sh
# assume you are root user
# sudo -s
apt-get update
apt-get install libgeos-dev
apt-get install python-pip
pip install -U -r requirements.txt
```

## Start Georest

Just run `./application.py`, it's Georest's default WSGI application.

To use Gunicorn/Gunicorn+NGINX, check
[gunicorn](http://gunicorn.org/#deployment).

## How to run tests

run `nosetests`
