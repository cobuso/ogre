from __future__ import absolute_import

import os
import random
import shutil
import string
import threading

import pytest
import virtualenvapi.manage

try:
    import sqlalchemy

    from .ogreserver import create_app
    from .ogreserver.models.user import User
    from .ogreserver.extensions.database import get_db, create_tables

    from wsgiref.simple_server import make_server
except ImportError:
    pass


@pytest.fixture(scope='session')
def app_config():
    return {
        'DEBUG': True,
        'BETA': False,
        'TESTING': True,
        'TESTING_LOG_PATH': 'ogreserver.log',

        'SECRET_KEY': 'its_a_secret',

        'AMQP_BROKER': 'amqp://dev:dev@localhost:5672/dev',
        'CELERY_DEFAULT_QUEUE': 'testing',
        'CELERY_DEFAULT_EXCHANGE_TYPE': 'direct',
        'CELERY_DEFAULT_ROUTING_KEY': 'testing',
        'CELERY_DEFAULT_EXCHANGE': 'testing',

        'AWS_ACCESS_KEY': '',
        'AWS_SECRET_KEY': '',
        'S3_BUCKET': 'oii-ogre-dev',

        'EBOOK_FORMATS': ['mobi','azw','pdf','epub'],
        'DOWNLOAD_LINK_EXPIRY': 10,

        'WHOOSH_BASE': 'test.db',
        'SQLALCHEMY_DATABASE_URI': 'mysql://root:eggs@localhost/test',
        'UPLOADED_EBOOKS_DEST': 'uploads',
        'UPLOADED_LOGS_DEST': 'logs',

        'RETHINKDB_DATABASE': 'test',
    }


@pytest.yield_fixture(scope='session')
def flask_app(app_config):
    app = create_app(app_config)
    yield app
    if os.path.exists(app_config['WHOOSH_BASE']):
        shutil.rmtree(app_config['WHOOSH_BASE'])


@pytest.fixture(scope='module')
def ogreserver(request, flask_app, datastore):
    server = make_server('', 6543, flask_app)
    app_thread = threading.Thread(target=server.serve_forever)
    app_thread.start()
    def fin():
        threading.Thread(target=server.shutdown).start()
    request.addfinalizer(fin)
    return app_thread


@pytest.yield_fixture(scope='session')
def mysqldb(request, flask_app):
    # use raw sqlalchemy for create/drop DB
    engine = sqlalchemy.create_engine('mysql://root:eggs@localhost/mysql')

    def run_query(sql):
        # get the internal connection obj, close the open transaction, then run
        conn = engine.connect()
        conn.execute('commit')
        conn.execute(sql)
        conn.close()

    # create a test database using sqlalchemy
    run_query('drop database if exists test')
    run_query('create database test')

    with flask_app.test_request_context():
        # init app tables into test database
        create_tables(flask_app)
        db_session = get_db(flask_app)
        yield db_session

    # cleanup the test mysql db
    run_query('drop database if exists test')


@pytest.fixture(scope='session')
def user(request, mysqldb):
    # create random username
    username = ''.join(random.choice(string.ascii_lowercase) for n in range(6))
    # create user in auth DB
    user = User(username, password=username, email='{}@example.com'.format(username))
    mysqldb.add(user)
    mysqldb.commit()
    return user


@pytest.fixture(scope='module')
def datastore(request):
    import rethinkdb as r
    conn = r.connect('localhost', 28015).repl()

    if 'test' in r.db_list().run(conn):
        r.db_drop('test').run(conn)

    # create test datebase
    r.db_create('test').run(conn)
    r.db('test').table_create('ebooks', primary_key='ebook_id').run()
    r.db('test').table_create('versions', primary_key='version_id').run()
    r.db('test').table_create('formats', primary_key='file_hash').run()
    r.db('test').table('versions').index_create('ebook_id').run()
    r.db('test').table('versions').index_wait('ebook_id').run()
    r.db('test').table('formats').index_create('version_id').run()
    r.db('test').table('formats').index_wait('version_id').run()

    # remove test database
    def fin():
        conn = r.connect('localhost', 28015)
        if 'test' in r.db_list().run(conn):
            r.db_drop('test').run(conn)
        conn.close()
    request.addfinalizer(fin)
    return r


@pytest.fixture(scope='session')
def client_config(user):
    return {
        'config_dir': None,
        'ebook_cache_path': None,
        'calibre_ebook_meta_bin': '/usr/bin/ebook-meta',
        'ebook_home': None,
        'providers': {},
        'username': user.username,
        'password': user.username,  # password=username during tests
        'host': 'localhost:6543',
        'verbose': False,
        'quiet': True,
    }


@pytest.fixture(scope='session')
def ebook_lib_path():
    # path where conftest.py resides + '/ebooks'
    return os.path.join(os.path.dirname(__file__), 'tests', 'ebooks')


@pytest.fixture(scope='function')
def virtualenv(tmpdir):
    # create a virtualenv in a tmpdir; pytest will clean up for us
    return virtualenvapi.manage.VirtualEnvironment(
        os.path.join(tmpdir.strpath, 'ogreclient')
    )
