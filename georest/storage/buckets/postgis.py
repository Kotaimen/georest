# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '6/17/14'

"""
    georest.storage.buckets.postgis
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    PostGIS Geo Feature Bucket.
"""

import sqlalchemy
import geoalchemy2
import geoalchemy2.shape
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, ForeignKey, Sequence
from sqlalchemy import BigInteger, String, DateTime, Boolean
from sqlalchemy.sql import select, func, bindparam, and_, text
from sqlalchemy.schema import CreateSchema, DropSchema
from sqlalchemy.pool import QueuePool
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.exc import IntegrityError

from ..exceptions import *
from ..bucket import FeatureBucket, FeatureMapper, Commit


class PostGISConnectionPool(object):
    def __init__(self,
                 host='localhost',
                 port=5432,
                 username='postgres',
                 password='123456',
                 database='test',
                 pool_size=5):
        connection_params = {
            'database': database,
            'username': username,
            'password': password,
            'host': host,
            'port': port
        }

        connection_template = \
            'postgresql+psycopg2://%(username)s:%(password)s' \
            '@%(host)s:%(port)s/%(database)s'

        connection_string = connection_template % connection_params

        self._engine = create_engine(
            connection_string, pool_size=pool_size, poolclass=QueuePool)

    def connect(self):
        return self._engine.connect()


class PostGISFeatureBucket(FeatureBucket):
    def __init__(self, name, pool, srid=None, max_revision_num=10):
        FeatureBucket.__init__(self, name)

        self._pool = pool
        self._srid = srid

        metadata = sqlalchemy.MetaData(schema=name)

        self.PROPERTIES_TABLE = Table(
            'properties', metadata,
            Column('id', BigInteger, primary_key=True, autoincrement=True),
            Column('properties', JSON, default={}),
        )

        self.METADATA_TABLE = Table(
            'metadata', metadata,
            Column('id', BigInteger, primary_key=True, autoincrement=True),
            Column('metadata', JSON, default={}),
        )

        self.GEOMETRY_TABLE = Table(
            'geometry', metadata,
            Column('id', BigInteger, primary_key=True, autoincrement=True),
            Column('geometry', geoalchemy2.Geometry('GEOMETRY', srid=srid)),
        )

        self.FEATURE_TABLE = Table(
            'features', metadata,
            Column('new_rev', String, primary_key=True),
            Column('old_rev', String, ForeignKey('features.new_rev')),
            Column('prop_id', BigInteger, ForeignKey('properties.id')),
            Column('meta_id', BigInteger, ForeignKey('metadata.id')),
            Column('geom_id', BigInteger, ForeignKey('geometry.id')),
            Column('deleted', Boolean, default=False),
            Column('timestamp', DateTime(timezone=True),
                   server_default=text(
                       "(CURRENT_TIMESTAMP AT TIME ZONE 'UTC')")),
        )

        self.HEAD_REF_TABLE = Table(
            'head_ref', metadata,
            Column('id', String, primary_key=True),
            Column('head_rev', String, ForeignKey('features.new_rev')),
        )

        self.FEATURE_KEY_SEQ = Sequence('global_id_seq', metadata=metadata)

        conn = self._pool.connect()
        with conn.begin() as trans:
            # metadata.drop_all(bind=conn)
            # conn.execute(DropSchema(name))
            conn.execute('''CREATE SCHEMA IF NOT EXISTS %s''' % name)
            metadata.create_all(bind=conn, checkfirst=True)

    def commit(self, name, mapper, parent=None):
        conn = self._pool.connect()
        with conn.begin() as trans:
            # if name exists and parent is None, set parent to head revision
            head_row = self._select_head(conn, name)
            if head_row and parent is None:
                parent = head_row.head_rev

            # insert components of the feature
            prop_id = self._insert_prop(conn, mapper.properties)
            meta_id = self._insert_meta(conn, mapper.metadata)
            geom_id = self._insert_geom(conn, mapper.wkt, mapper.srid)

            # insert a new revision of the feature
            try:
                inserted = self._insert_feature(
                    conn, prop_id, meta_id, geom_id, parent_rev=parent)
            except sqlalchemy.exc.IntegrityError:
                raise ParentRevisionNotFound(name, parent_rev=parent)

            # update or insert the head reference
            try:
                self._upsert_head(
                    conn, name, inserted.new_rev, inserted.old_rev)
            except sqlalchemy.exc.IntegrityError:
                raise NotHeadRevision(name, parent_rev=parent)

            commit = Commit(
                name=name,
                revision=inserted.new_rev,
                parent_revision=inserted.old_rev,
                timestamp=inserted.timestamp
            )
            return commit

    def checkout(self, name, revision=None):
        conn = self._pool.connect()
        with conn.begin() as trans:

            head_row = self._select_head(conn, name)
            if head_row is None:
                raise FeatureNotFound(name, revision)
            if revision is None:
                revision = head_row.head_rev

            feature_row = self._select_feature(conn, name, revision)
            if feature_row is None or feature_row.deleted:
                raise FeatureNotFound(name, revision)

            prop_row = self._select_prop(conn, feature_row.prop_id)
            meta_row = self._select_meta(conn, feature_row.meta_id)
            geom_row = self._select_geom(conn, feature_row.geom_id)

            shapely_geom = geoalchemy2.shape.to_shape(geom_row.geometry)
            srid = geom_row.geometry.srid

            commit = Commit(
                name=name,
                revision=feature_row.new_rev,
                parent_revision=feature_row.old_rev,
                timestamp=feature_row.timestamp
            )

            mapper = FeatureMapper(
                properties=prop_row.properties,
                metadata=meta_row.metadata,
                wkt=shapely_geom.wkt,
                srid=srid
            )
            return commit, mapper

    def head(self, name):
        conn = self._pool.connect()
        with conn.begin() as trans:
            head_row = self._select_head(conn, name)
            if not head_row:
                raise FeatureNotFound(name)

            feature_row = self._select_feature(conn, name, head_row.head_rev)
            commit = Commit(
                name=name,
                revision=feature_row.new_rev,
                parent_revision=feature_row.old_rev,
                timestamp=feature_row.timestamp
            )
            return commit

    def status(self, name, revision=None):
        if revision is None:
            return self.head(name)

        conn = self._pool.connect()
        with conn.begin() as trans:
            feature_row = self._select_feature(conn, name, revision)
            if feature_row is None:
                raise FeatureNotFound(name, revision)

            commit = Commit(
                name=name,
                revision=feature_row.new_rev,
                parent_revision=feature_row.old_rev,
                timestamp=feature_row.timestamp
            )
            return commit


    def remove(self, name, parent=None):
        conn = self._pool.connect()
        with conn.begin() as trans:
            head_row = self._select_head(conn, name)
            if head_row is None:
                raise FeatureNotFound(name, parent)
            if parent is None:
                parent = head_row.head_rev
            if parent != head_row.head_rev:
                raise NotHeadRevision(name, parent_rev=parent)

            # insert a new revision of the feature
            prop_id = meta_id = geom_id = None
            try:
                inserted = self._insert_feature(
                    conn, prop_id, meta_id, geom_id, parent_rev=parent,
                    deleted=True)
            except sqlalchemy.exc.IntegrityError as e:
                raise ParentRevisionNotFound(name, parent)

            try:
                self._upsert_head(
                    conn, name, inserted.new_rev, inserted.old_rev)
            except sqlalchemy.exc.IntegrityError:
                raise NotHeadRevision(name, parent_rev=parent)

            commit = Commit(
                name=name,
                revision=inserted.new_rev,
                parent_revision=inserted.old_rev,
                timestamp=inserted.timestamp
            )
            return commit

    def make_random_name(self):
        conn = self._pool.connect()
        with conn.begin() as trans:
            ret = conn.execute(select([self.FEATURE_KEY_SEQ.next_value()]))
            return 'feature%d' % ret.scalar()

    def _insert_prop(self, conn, prop):
        stmt = self.PROPERTIES_TABLE.insert()
        result = conn.execute(stmt, properties=prop)
        prop_id = result.inserted_primary_key[0]
        return prop_id

    def _insert_meta(self, conn, meta):
        stmt = self.METADATA_TABLE.insert()
        result = conn.execute(stmt, metadata=meta)
        meta_id = result.inserted_primary_key[0]
        return meta_id

    def _insert_geom(self, conn, wkt, srid):
        stmt = self.GEOMETRY_TABLE.insert()
        result = conn.execute(
            stmt, geometry=geoalchemy2.WKTElement(wkt, srid))
        geom_id = result.inserted_primary_key[0]
        return geom_id

    def _insert_feature(
            self, conn, prop_id, meta_id, geom_id, parent_rev, deleted=False):
        insert_feature = self.FEATURE_TABLE.insert().values(
            new_rev=func.encode(
                func.digest(bindparam('new_rev'), 'sha1'), 'hex')
        ).returning(
            self.FEATURE_TABLE.c.new_rev,
            self.FEATURE_TABLE.c.old_rev,
            self.FEATURE_TABLE.c.timestamp
        )

        result = conn.execute(
            insert_feature,
            prop_id=prop_id,
            meta_id=meta_id,
            geom_id=geom_id,
            old_rev=parent_rev,
            new_rev='%s%s%s%s' % (prop_id, meta_id, geom_id, parent_rev),
            deleted=deleted
        )
        inserted = result.fetchone()
        return inserted

    def _upsert_head(self, conn, name, head_rev, parent_rev):
        update_head = self.HEAD_REF_TABLE.update().where(
            and_(
                self.HEAD_REF_TABLE.c.id == name,
                self.HEAD_REF_TABLE.c.head_rev == parent_rev
            )
        )

        result = conn.execute(update_head, head_rev=head_rev)
        if result.rowcount == 0:
            insert_head = self.HEAD_REF_TABLE.insert()
            conn.execute(insert_head, id=name, head_rev=head_rev)


    def _select_head(self, conn, name):
        select_head = self.HEAD_REF_TABLE.select().where(
            self.HEAD_REF_TABLE.c.id == name
        )

        head_row = conn.execute(select_head).fetchone()
        return head_row

    def _select_feature(self, conn, name, rev):
        select_feature = self.FEATURE_TABLE.select().where(
            self.FEATURE_TABLE.c.new_rev == rev
        )
        feature_row = conn.execute(select_feature).fetchone()
        return feature_row

    def _select_prop(self, conn, prop_id):
        select_prop = self.PROPERTIES_TABLE.select().where(
            self.PROPERTIES_TABLE.c.id == prop_id
        )
        prop_row = conn.execute(select_prop).fetchone()
        return prop_row

    def _select_meta(self, conn, meta_id):
        select_meta = self.METADATA_TABLE.select().where(
            self.METADATA_TABLE.c.id == meta_id
        )
        meta_row = conn.execute(select_meta).fetchone()
        return meta_row

    def _select_geom(self, conn, geom_id):
        select_geom = self.GEOMETRY_TABLE.select().where(
            self.GEOMETRY_TABLE.c.id == geom_id
        )
        geom_row = conn.execute(select_geom).fetchone()
        return geom_row
