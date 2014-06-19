# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '6/10/14'

import time
import sqlalchemy
import geoalchemy2
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, ForeignKey, Sequence
from sqlalchemy import BigInteger, String, DateTime
from sqlalchemy.sql import select, func, bindparam, and_
from sqlalchemy.pool import QueuePool
from sqlalchemy.dialects.postgresql import JSON

from ..geo import Key, Feature, SpatialReference, Geometry, Metadata

from .exceptions import *
from .storage import FeatureStorage, StorageResponse

metadata = sqlalchemy.MetaData()

FEATURE_GEOMETRY_TABLE = Table(
    'feature_geometry', metadata,
    Column('id', BigInteger, primary_key=True, index=True, unique=True,
           autoincrement=True),
    Column('geometry', geoalchemy2.Geometry('GEOMETRY', srid=4326))
)

FEATURE_PROPERTIES_TABLE = Table(
    'feature_properties', metadata,
    Column('id', BigInteger, primary_key=True, index=True, unique=True,
           autoincrement=True),
    Column('properties', JSON, nullable=False, default={})
)

FEATURE_METADATA_TABLE = Table(
    'feature_metadata', metadata,
    Column('id', BigInteger, primary_key=True, index=True, unique=True,
           autoincrement=True),
    Column('metadata', JSON, nullable=False, default={})
)

FEATURE_VERSION_TABLE = Table(
    'feature_version', metadata,
    Column('new_version', String, primary_key=True, index=True, unique=True),
    Column('old_version', String, ForeignKey('feature_version.new_version')),
    Column('metadata_id', BigInteger,
           ForeignKey('feature_metadata.id')),
    Column('properties_id', BigInteger,
           ForeignKey('feature_properties.id')),
    Column('geometry_id', BigInteger,
           ForeignKey('feature_geometry.id')),
    Column('status', String, default='avalable')
)

FEATURE_TABLE = Table(
    'features', metadata,
    Column('id', String, primary_key=True, index=True, unique=True),
    Column('top_version', String, ForeignKey('feature_version.new_version')),
)

FEATURE_KEY_SEQ = Sequence('feature_key_seq')


class FeatureMapper(object):
    def __init__(self, key=None, metadata=None, properties=None,
                 geometry=None):
        self.storage_key = key
        self.metadata = metadata
        self.properties = properties
        self.geometry = geometry


class _Proxy(object):
    def __init__(self, conn):
        self._conn = conn

    def random_num(self):
        ret = self._conn.execute(select([FEATURE_KEY_SEQ.next_value()]))
        return ret.scalar()

    def insert_metadata(self, metadata):
        insert_stmt = FEATURE_METADATA_TABLE.insert().returning(
            FEATURE_METADATA_TABLE.c.id,
            FEATURE_METADATA_TABLE.c.metadata
        )
        ret = self._conn.execute(insert_stmt, metadata=metadata).fetchone()
        return ret

    def select_metadata(self, key):
        select_stmt = FEATURE_METADATA_TABLE.select().where(
            FEATURE_METADATA_TABLE.c.id == key
        )
        ret = self._conn.execute(select_stmt).fetchone()
        return ret

    def insert_properties(self, properties):
        insert_stmt = FEATURE_PROPERTIES_TABLE.insert().returning(
            FEATURE_PROPERTIES_TABLE.c.id,
            FEATURE_PROPERTIES_TABLE.c.properties
        )
        ret = self._conn.execute(insert_stmt, properties=properties).fetchone()
        return ret

    def select_properties(self, key):
        select_stmt = FEATURE_PROPERTIES_TABLE.select().where(
            FEATURE_PROPERTIES_TABLE.c.id == key
        )
        ret = self._conn.execute(select_stmt).fetchone()
        return ret

    def insert_geometry(self, geometry):
        insert_stmt = FEATURE_GEOMETRY_TABLE.insert().returning(
            FEATURE_GEOMETRY_TABLE.c.id,
            FEATURE_GEOMETRY_TABLE.c.geometry
        )
        ret = self._conn.execute(insert_stmt, geometry=geometry).fetchone()
        return ret

    def select_geometry(self, key):
        select_stmt = FEATURE_GEOMETRY_TABLE.select().where(
            FEATURE_GEOMETRY_TABLE.c.id == key
        )
        ret = self._conn.execute(select_stmt).fetchone()
        return ret

    def insert_version(self, metadata_id, properties_id, geometry_id,
                       old_version, status):
        insert_stmt = FEATURE_VERSION_TABLE.insert().values(
            new_version=func.encode(func.digest(
                bindparam('ver'), 'sha1'), 'hex')
        ).returning(
            FEATURE_VERSION_TABLE.c.new_version,
            FEATURE_VERSION_TABLE.c.old_version,
            FEATURE_VERSION_TABLE.c.metadata_id,
            FEATURE_VERSION_TABLE.c.properties_id,
            FEATURE_VERSION_TABLE.c.geometry_id
        )

        ret = self._conn.execute(
            insert_stmt,
            ver='%s%s%s%s' % (metadata_id, properties_id, geometry_id, status),
            old_version=old_version,
            metadata_id=metadata_id,
            properties_id=properties_id,
            geometry_id=geometry_id,
            status=status
        ).fetchone()

        return ret

    def select_version(self, version):
        select_stmt = FEATURE_VERSION_TABLE.select().where(
            FEATURE_VERSION_TABLE.c.new_version == version
        )
        ret = self._conn.execute(select_stmt).fetchone()
        return ret

    def insert_feature(self, key, top_version):
        insert_stmt = FEATURE_TABLE.insert().returning(
            FEATURE_TABLE.c.id,
            FEATURE_TABLE.c.top_version,
        )
        ret = self._conn.execute(
            insert_stmt, id=key, top_version=top_version).fetchone()
        return ret

    def update_feature(self, key, top_version, base_version):
        update_stmt = FEATURE_TABLE \
            .update() \
            .where(
            and_(FEATURE_TABLE.c.id == key,
                 FEATURE_TABLE.c.top_version == base_version)
        ) \
            .returning(
            FEATURE_TABLE.c.id,
            FEATURE_TABLE.c.top_version,
        )
        ret = self._conn.execute(
            update_stmt, top_version=top_version
        ).fetchone()
        return ret

    def select_feature(self, key):
        select_stmt = FEATURE_TABLE.select().where(
            FEATURE_TABLE.c.id == key
        )
        ret = self._conn.execute(select_stmt).fetchone()
        return ret


class PostgisFeatureStorage(FeatureStorage):
    def __init__(self,
                 host='localhost',
                 port=5432,
                 username='postgres',
                 password='123456',
                 database='mydb',
                 create_table=False):
        conn_params = {
            'database': database,
            'username': username,
            'password': password,
            'host': host,
            'port': port
        }
        conn_string = \
            'postgresql+psycopg2://%(username)s:%(password)s' \
            '@%(host)s:%(port)s/%(database)s' % conn_params

        engine = create_engine(conn_string, echo=True,
                               poolclass=QueuePool, pool_size=10)

        if create_table:
            metadata.drop_all(bind=engine)
            metadata.create_all(bind=engine, checkfirst=True)

        self._db = engine

    def put_feature(self, key, feature, revision=None, fetch=False):
        srid = feature.crs.srid
        if srid != 4326:
            raise InvalidFeature('srid=%s' % srid)

        with self._db.begin() as conn:
            proxy = _Proxy(conn)
            mapper = self._make_mapper_from_feature(feature)

            bucket, name = key
            if name is None:
                name = str(proxy.random_num())

            new_key = Key.make_key(bucket=bucket, name=name)

            mapper.storage_key = new_key.qualified_name

            feature_entry = proxy.select_feature(mapper.storage_key)

            top_version = None
            if feature_entry:
                top_version = feature_entry.top_version

            if revision and revision != top_version:
                raise ConflictVersion(revision)

            properties_entry = proxy.insert_properties(mapper.properties)
            metadata_entry = proxy.insert_metadata(mapper.metadata)
            geometry_entry = proxy.insert_geometry(mapper.geometry)

            version_entry = proxy.insert_version(
                metadata_entry.id,
                properties_entry.id,
                geometry_entry.id,
                old_version=top_version,
                status='available'
            )

            if feature_entry is not None:
                feature_entry = proxy.update_feature(
                    feature_entry.id,
                    version_entry.new_version,
                    version_entry.old_version
                )
                if feature_entry is None:
                    raise ConflictVersion()
            else:
                feature_entry = proxy.insert_feature(
                    mapper.storage_key,
                    version_entry.new_version
                )

            result = StorageResponse(
                key=new_key,
                revision=feature_entry.top_version,
                feature=feature if fetch else None,
                timestamp=time.time()
            )

            return result

    def get_feature(self, key, revision=None):
        with self._db.begin() as conn:
            proxy = _Proxy(conn)

            storage_key = key.qualified_name

            feature_entry = proxy.select_feature(storage_key)
            if feature_entry is None:
                raise FeatureNotFound('key: %s, version: %s' % (key, revision))

            if revision is None:
                revision = feature_entry.top_version

            version_entry = proxy.select_version(revision)
            if version_entry is None:
                raise FeatureNotFound('key: %s, version: %s' % (key, revision))

            if version_entry.status == 'deleted':
                raise FeatureNotFound('key: %s, version: %s' % (key, revision))

            metadata_entry = proxy.select_metadata(version_entry.metadata_id)
            properties_entry = proxy.select_properties(
                version_entry.properties_id)
            geometry_entry = proxy.select_geometry(version_entry.geometry_id)

            crs = SpatialReference(srid=4326)
            geometry = Geometry.build_geometry(geometry_entry.geometry.data)

            feature = Feature(
                key=key,
                crs=crs,
                metadata=Metadata(**metadata_entry.metadata),
                properties=properties_entry.properties,
                geometry=geometry,
            )

            result = StorageResponse(
                key=feature.key,
                revision=revision,
                feature=feature,
                timestamp=time.time()
            )

            return result

    def delete_feature(self, key, revision=None, fetch=False):
        with self._db.begin() as conn:
            proxy = _Proxy(conn)

            name = key.qualified_name

            feature_entry = proxy.select_feature(name)
            if feature_entry is None:
                return StorageResponse(success=True)

            if revision and revision != feature_entry.top_version:
                raise ConflictVersion(revision)

            old = proxy.select_version(feature_entry.top_version)

            version_entry = proxy.insert_version(
                old.metadata_id, old.properties_id, old.geometry_id,
                feature_entry.top_version, 'deleted')

            feature_entry = proxy.update_feature(name,
                                                 version_entry.new_version,
                                                 version_entry.old_version)

            metadata_entry = proxy.select_metadata(version_entry.metadata_id)
            properties_entry = proxy.select_properties(
                version_entry.properties_id)
            geometry_entry = proxy.select_geometry(version_entry.geometry_id)

            crs = SpatialReference(srid=4326)
            geometry = Geometry.build_geometry(geometry_entry.geometry.data)

            feature = Feature(
                key=key,
                crs=crs,
                metadata=Metadata(**metadata_entry.metadata),
                properties=properties_entry.properties,
                geometry=geometry,
            )

            result = StorageResponse(
                key=feature.key,
                revision=feature_entry.top_version,
                feature=feature if fetch else None,
                timestamp=time.time()
            )
            return result

    def _make_mapper_from_feature(self, feature):

        metadata = feature.metadata._asdict()
        properties = dict(feature.properties)
        geometry = 'SRID=%d;%s' % (feature.crs.srid, feature.geometry.wkt)

        mapper = FeatureMapper(metadata=metadata, properties=properties,
                               geometry=geometry)
        return mapper



