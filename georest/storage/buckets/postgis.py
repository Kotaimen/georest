# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '6/17/14'

"""
    georest.storage.buckets.postgis
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    PostGIS Geo Feature Bucket.
"""

import uuid
import ujson
import sqlalchemy
import geoalchemy2
import geoalchemy2.shape
from sqlalchemy import create_engine
from sqlalchemy import PrimaryKeyConstraint, Table, Column, DDL, event
from sqlalchemy import BigInteger, String, DateTime
from sqlalchemy.sql import func, bindparam, select, and_
from sqlalchemy.pool import QueuePool
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.exc import IntegrityError

from ..exceptions import *
from ..storage import FeatureStorage
from ..bucket import FeatureBucket, FeatureMapper, Commit


def qualified_schema_name(name):
    return 'bucket_%s' % name


class PostGISFeatureStorage(FeatureStorage):
    support_version = True

    def __init__(self,
                 host='localhost',
                 port=5432,
                 username='postgres',
                 password='123456',
                 database='test',
                 pool_size=5,
                 debug=False):
        conn_params = {
            'database': database,
            'username': username,
            'password': password,
            'host': host,
            'port': port
        }

        conn_template = \
            'postgresql+psycopg2://' \
            '%(username)s:%(password)s@%(host)s:%(port)s/%(database)s'

        conn_string = conn_template % conn_params

        self._engine = create_engine(
            conn_string,
            pool_size=pool_size,
            poolclass=QueuePool,
            json_serializer=ujson.dumps,
            json_deserializer=ujson.loads,
            echo=debug,
        )

    def describe(self):
        import psycopg2

        description = {
            'SQLAlchemy': 'SQLAlchemy (%s)' % sqlalchemy.__version__,
            'GeoAlchemy2': 'GeoAlchemy2 (%s)' % '0.2.4',
            'psycopg2': 'psycopg2 (%s)' % psycopg2.__version__,
        }

        description.update(FeatureStorage.describe(self))
        return description

    def create_bucket(self, name, overwrite=False, **kwargs):
        srid = kwargs.get('srid', 4326)

        schema_name = qualified_schema_name(name)

        if self.has_bucket(name):
            if not overwrite:
                raise DuplicatedBucket(name)
            self._drop_schema(schema_name)

        self._create_schema(schema_name)

        bucket = PostGISFeatureBucket(
            name, self._engine, schema=schema_name, srid=srid)

        return bucket

    def get_bucket(self, name):
        schema_name = qualified_schema_name(name)

        srid = self._inspect_srid(schema_name)
        if srid is None:
            raise BucketNotFound(name)

        bucket = PostGISFeatureBucket(
            name, self._engine, schema=schema_name, srid=srid)

        return bucket

    def has_bucket(self, name):
        schema_name = qualified_schema_name(name)
        srid = self._inspect_srid(schema_name)
        return srid is not None

    def delete_bucket(self, name):
        schema_name = qualified_schema_name(name)
        if not self.has_bucket(name):
            raise BucketNotFound(name)
        self._drop_schema(schema_name)
        return True

    def _create_schema(self, schema_name):
        with self._engine.begin() as conn:
            conn.execute(
                '''CREATE SCHEMA IF NOT EXISTS "%s";''' % schema_name)

    def _drop_schema(self, schema_name):
        with self._engine.begin() as conn:
            conn.execute(
                '''DROP SCHEMA IF EXISTS "%s" CASCADE;''' % schema_name)


    def _inspect_srid(self, bucket_name):
        with self._engine.begin() as conn:
            srid = conn.execute(
                '''SELECT * FROM geometry_columns WHERE f_table_schema=%(name)s''',
                name=bucket_name).scalar()
            return srid


class PostGISFeatureBucket(FeatureBucket):
    def __init__(self, name, engine, schema='', srid=None, revision_cap=10):
        FeatureBucket.__init__(self, name)

        self._engine = engine
        self._schema = schema
        self._srid = srid
        self._revision_cap = revision_cap

        metadata = sqlalchemy.MetaData(schema=self._schema)

        self.FEATURE_TABLE = Table(
            'feature', metadata,
            Column('name', String, index=True),
            Column('properties', JSON, default=None),
            Column('metadata', JSON, default=None),
            Column('geometry', geoalchemy2.Geometry('GEOMETRY', srid=4326)),
            Column('create_at', DateTime, nullable=False),
            Column('expire_at', DateTime, nullable=False),
            Column('revision', String, index=True),
            PrimaryKeyConstraint('name', 'expire_at')
        )

        create_feature_view = DDL("""
            CREATE OR REPLACE VIEW %(schema)s.current_feature AS
                SELECT * FROM %(fullname)s WHERE expire_at = 'infinity';
        """)

        create_time_travel_before_func = DDL("""
            CREATE OR REPLACE FUNCTION %(schema)s.time_travel_before()
            RETURNS trigger AS
            $BODY$
            DECLARE
                time_now TIMESTAMP;
                revision VARCHAR;
            BEGIN
                time_now = now();
                revision = encode(public.digest(CAST(time_now AS text), 'sha1'), 'hex');

                IF (TG_OP = 'UPDATE' OR TG_OP = 'DELETE') THEN
                    IF OLD.expire_at != 'infinity' THEN
                        RAISE EXCEPTION 'Cannot %% old row', TG_OP;
                    END IF;

                    EXECUTE 'SELECT * FROM ' || format('%%s.%%s', TG_TABLE_SCHEMA, TG_TABLE_NAME)::regclass || ' WHERE ctid = $1 FOR UPDATE' USING OLD.ctid;

                    IF (TG_OP = 'UPDATE') THEN
                        NEW.create_at := time_now;
                        NEW.expire_at := 'infinity';
                        NEW.revision := revision;
                        RETURN NEW;

                    ELSIF (TG_OP = 'DELETE') THEN
                        RETURN OLD;

                    ELSE
                        RETURN NULL;

                    END IF;

                ELSIF (TG_OP = 'INSERT') THEN
                    IF NEW.create_at IS NULL THEN
                        NEW.create_at := time_now;
                    END IF;

                    IF NEW.expire_at IS NULL THEN
                        NEW.expire_at := 'infinity';
                    END IF;

                    IF NEW.revision IS NULL THEN
                        NEW.revision := revision;
                    END IF;

                    RETURN NEW;

                ELSE
                    RETURN NULL;

                END IF;

            END;
            $BODY$
            LANGUAGE plpgsql;
        """)

        create_time_travel_after_func = DDL("""
            CREATE OR REPLACE FUNCTION %(schema)s.time_travel_after()
            RETURNS trigger AS
            $BODY$
            DECLARE
                temp_row RECORD;
            BEGIN

                IF (TG_OP = 'UPDATE' OR TG_OP = 'DELETE') THEN

                    temp_row := OLD;

                    IF (TG_OP = 'UPDATE') THEN
                        temp_row.expire_at := NEW.create_at;
                    ELSIF (TG_OP = 'DELETE') THEN
                        temp_row.expire_at := now();
                    END IF;

                    EXECUTE 'INSERT INTO  ' || format('%%s.%%s', TG_TABLE_SCHEMA, TG_TABLE_NAME)::regclass || ' SELECT $1.*' USING temp_row;

                END IF;

                RETURN NULL;

            END;
            $BODY$
            LANGUAGE plpgsql;
        """)

        create_time_travel_before_trigger = DDL("""
            CREATE TRIGGER "10_time_travel_before_trigger"
            BEFORE INSERT OR UPDATE OR DELETE
            ON %(fullname)s
            FOR EACH ROW
            EXECUTE PROCEDURE %(schema)s.time_travel_before();
        """)

        create_time_travel_after_trigger = DDL("""
            CREATE TRIGGER "11_time_travel_after_trigger"
            AFTER UPDATE OR DELETE
            ON %(fullname)s
            FOR EACH ROW
            EXECUTE PROCEDURE %(schema)s.time_travel_after();
        """)

        # register views
        event.listen(
            self.FEATURE_TABLE,
            "after_create",
            create_feature_view,
        )

        # # register functions
        event.listen(
            self.FEATURE_TABLE,
            "after_create",
            create_time_travel_before_func,
        )
        event.listen(
            self.FEATURE_TABLE,
            "after_create",
            create_time_travel_after_func,
        )
        event.listen(
            self.FEATURE_TABLE,
            "after_create",
            create_time_travel_before_trigger,
        )

        event.listen(
            self.FEATURE_TABLE,
            "after_create",
            create_time_travel_after_trigger,
        )

        metadata.create_all(bind=engine, checkfirst=True)

    def commit(self, name, mapper, parent=None):
        with self._engine.begin() as conn:

            top = self._select_top_revision(conn, name)
            if top:
                if parent is None:
                    inserted = self._update(conn, name, mapper)
                else:
                    try:
                        inserted = self._update_against_parent(
                            conn, name, mapper, parent)
                    except sqlalchemy.exc.InternalError as e:
                        raise NotHeadRevision(name, parent, e)
            else:
                if parent is not None:
                    raise ParentRevisionNotFound(name, parent)

                inserted = self._insert(conn, name, mapper)

            commit = Commit(
                name=inserted.name,
                revision=inserted.revision,
                create_at=inserted.create_at,
                expire_at=inserted.expire_at,
            )

            return commit

    def checkout(self, name, revision=None):
        with self._engine.begin() as conn:
            if revision is not None:
                selected = self._select(conn, name, revision)
                if selected is None:
                    raise FeatureNotFound(name, revision)

            else:
                selected = self._select_top(conn, name)
                if selected is None:
                    raise FeatureNotFound(name, revision)

            commit = Commit(
                name=selected.name,
                revision=selected.revision,
                create_at=selected.create_at,
                expire_at=selected.expire_at,
            )

            mapper = FeatureMapper(
                properties=selected.properties,
                metadata=selected.metadata,
                wkt=geoalchemy2.shape.to_shape(selected.geometry).wkt,
                srid=selected.geometry.srid
            )

            return commit, mapper

    def status(self, name, revision=None):
        with self._engine.begin() as conn:
            if revision is None:
                selected = self._select_top_revision(conn, name)
            else:
                selected = self._select_revision(conn, name, revision)

            if selected is None:
                raise FeatureNotFound(name, revision)

            commit = Commit(
                name=selected.name,
                revision=selected.revision,
                create_at=selected.create_at,
                expire_at=selected.expire_at,
            )
            return commit


    def remove(self, name, parent=None):
        with self._engine.begin() as conn:
            if parent is None:
                deleted = self._delete(conn, name)
            else:
                try:
                    deleted = self._delete_agains_parent(conn, name, parent)
                except sqlalchemy.exc.InternalError as e:
                    raise NotHeadRevision(name, parent, e)

            selected = self._select_revision(conn, name, deleted.revision)

            commit = Commit(
                name=deleted.name,
                revision=None,  # deleted.revision,
                create_at=deleted.create_at,
                expire_at=selected.expire_at,
            )
            return commit

    def make_random_name(self):
        name = uuid.uuid4().hex
        return name

    def _insert(self, conn, name, mapper):
        insert_stmt = self.FEATURE_TABLE.insert().returning(
            self.FEATURE_TABLE.c.name,
            self.FEATURE_TABLE.c.create_at,
            self.FEATURE_TABLE.c.expire_at,
            self.FEATURE_TABLE.c.revision,
        )

        inserted = conn.execute(
            insert_stmt,
            name=name,
            properties=mapper.properties,
            metadata=mapper.metadata,
            geometry=geoalchemy2.WKTElement(mapper.wkt, mapper.srid),
        ).fetchone()
        return inserted

    def _update(self, conn, name, mapper):
        update_stmt = self.FEATURE_TABLE.update().where(
            and_(
                self.FEATURE_TABLE.c.name == name,
                self.FEATURE_TABLE.c.expire_at == 'infinity',
            )
        ).returning(
            self.FEATURE_TABLE.c.name,
            self.FEATURE_TABLE.c.create_at,
            self.FEATURE_TABLE.c.expire_at,
            self.FEATURE_TABLE.c.revision,
        )

        updated = conn.execute(
            update_stmt,
            properties=mapper.properties,
            metadata=mapper.metadata,
            geometry=geoalchemy2.WKTElement(mapper.wkt, mapper.srid),
        ).fetchone()
        return updated

    def _update_against_parent(self, conn, name, mapper, parent):
        update_stmt = self.FEATURE_TABLE.update().where(
            and_(
                self.FEATURE_TABLE.c.name == name,
                self.FEATURE_TABLE.c.revision == parent,
            )
        ).returning(
            self.FEATURE_TABLE.c.name,
            self.FEATURE_TABLE.c.create_at,
            self.FEATURE_TABLE.c.expire_at,
            self.FEATURE_TABLE.c.revision,
        )

        updated = conn.execute(
            update_stmt,
            properties=mapper.properties,
            metadata=mapper.metadata,
            geometry=geoalchemy2.WKTElement(mapper.wkt, mapper.srid),
        ).fetchone()
        return updated

    def _delete(self, conn, name):
        delete_stmt = self.FEATURE_TABLE.delete().where(
            and_(
                self.FEATURE_TABLE.c.name == name,
                self.FEATURE_TABLE.c.expire_at == 'infinity',
            )
        ).returning(
            self.FEATURE_TABLE.c.name,
            self.FEATURE_TABLE.c.create_at,
            self.FEATURE_TABLE.c.expire_at,
            self.FEATURE_TABLE.c.revision,
        )

        deleted = conn.execute(delete_stmt).fetchone()
        return deleted

    def _delete_agains_parent(self, conn, name, parent):
        delete_stmt = self.FEATURE_TABLE.delete().where(
            and_(
                self.FEATURE_TABLE.c.name == name,
                self.FEATURE_TABLE.c.revision == parent,
            )
        ).returning(
            self.FEATURE_TABLE.c.name,
            self.FEATURE_TABLE.c.create_at,
            self.FEATURE_TABLE.c.expire_at,
            self.FEATURE_TABLE.c.revision,
        )

        deleted = conn.execute(delete_stmt).fetchone()
        return deleted

    def _select(self, conn, name, revision):
        select_stmt = select([
            self.FEATURE_TABLE.c.name,
            self.FEATURE_TABLE.c.properties,
            self.FEATURE_TABLE.c.metadata,
            self.FEATURE_TABLE.c.geometry,
            self.FEATURE_TABLE.c.create_at,
            self.FEATURE_TABLE.c.expire_at,
            self.FEATURE_TABLE.c.revision,
        ]).where(
            and_(
                self.FEATURE_TABLE.c.name == name,
                self.FEATURE_TABLE.c.revision == revision
            )
        )

        selected = conn.execute(select_stmt).fetchone()
        return selected

    def _select_revision(self, conn, name, revision):
        select_stmt = select([
            self.FEATURE_TABLE.c.name,
            self.FEATURE_TABLE.c.create_at,
            self.FEATURE_TABLE.c.expire_at,
            self.FEATURE_TABLE.c.revision,
        ]).where(
            and_(
                self.FEATURE_TABLE.c.name == name,
                self.FEATURE_TABLE.c.revision == revision,
            )
        )

        selected = conn.execute(select_stmt).fetchone()
        return selected

    def _select_top(self, conn, name):
        select_stmt = select([
            self.FEATURE_TABLE.c.name,
            self.FEATURE_TABLE.c.properties,
            self.FEATURE_TABLE.c.metadata,
            self.FEATURE_TABLE.c.geometry,
            self.FEATURE_TABLE.c.create_at,
            self.FEATURE_TABLE.c.expire_at,
            self.FEATURE_TABLE.c.revision,
        ]).where(
            and_(
                self.FEATURE_TABLE.c.name == name,
                self.FEATURE_TABLE.c.expire_at == 'infinity',
            )
        )

        selected = conn.execute(select_stmt).fetchone()
        return selected

    def _select_top_revision(self, conn, name):
        select_stmt = select([
            self.FEATURE_TABLE.c.name,
            self.FEATURE_TABLE.c.create_at,
            self.FEATURE_TABLE.c.expire_at,
            self.FEATURE_TABLE.c.revision,
        ]).where(
            and_(
                self.FEATURE_TABLE.c.name == name,
                self.FEATURE_TABLE.c.expire_at == 'infinity',
            )
        )

        selected = conn.execute(select_stmt).fetchone()
        return selected
