# GeoRest

A restful, schema-less, searchable Geo-spatial Feature object storage.

Note: still in development, only features required by geoevent system 
is implemented.

## Features

- Restful API
- GeoJSON as exchange format
- Spatial operation/algorithm RPC
- Object based revision
- Simple spatial query support (todo)
- Switchable storage backend
    - postgis
    - memcached
    - mongodb (todo)
    - s3 (todo)
- Entity tracking support (todo)
- Builtin monitoring (todo)

## Install on Ubuntu 12.04+ 

```sh
sudo apt-get update
sudo apt-get install g++ libgeos-dev libpq-dev python-dev python-pip build-essential  
sudo pip install -r requirements.txt
```

## Install on Mac using homebrew

Assuming use brew python instead of system python. 

```sh
brew install geos libpq python 
pip install -r requirements.txt
```

## Configuration and Running

For debug/test, just run `./manage.py`.

Or run via gunicorn: 
    
    gunicorn georest.app -w 2

Recommended production deployment is use `nginx` + `Gunicorn`, 
see [offcial manual](http://gunicorn.org/#deployment).

We uses `flask` instance configuration so default setting is 
    
    ./instance/setting.py
    
(if you didn't install `georest` into system python or virtual environment).
    

## Unittest

Simply run:
    
    nosetests
    
This will also generate a coverage report, note using `unittest` runner in
an IDE is also OK.

You have to setup a local memcache/postgres server and several 
environment variables to be able to run the complete test.

## API Document

Check `./doc`
