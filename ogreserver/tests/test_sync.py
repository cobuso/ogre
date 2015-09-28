from __future__ import absolute_import

from ..models.datastore import DataStore


def test_sync_duplicate(flask_app, datastore, user):
    ebooks_dict = {
        u"H. C.\u0006Andersen\u0007Andersen's Fairy Tales": {
            'format': 'epub',
            'file_hash': '38b3fc3aa7fe67e76f0d8b248e62b940',
            'owner': 'mafro',
            'size': 139654
        },
    }

    # create the datastore and run a sync
    ds = DataStore(flask_app.config, flask_app.logger)
    syncd_books = ds.update_library(ebooks_dict, user)

    # assert book is new
    key, data = syncd_books.items()[0]
    assert data['new'] is True, "wasn't stored on first sync"
    assert data['dupe'] is False, 'book should not be a duplicate'

    # sync again
    syncd_books = ds.update_library(ebooks_dict, user)

    # assert book is duplicate
    key, data = syncd_books.items()[0]
    assert data['dupe'] is True, 'book should be a duplicate'


def test_sync_ebook_update(flask_app, datastore, user):
    ebooks_dict = {
        u"H. C.\u0006Andersen\u0007Andersen's Fairy Tales": {
            'format': 'epub',
            'file_hash': 'b889dec977aef12c6973acc2cf5b8590',
            'owner': 'mafro',
            'size': 139654
        },
    }

    # create the datastore and run a sync
    ds = DataStore(flask_app.config, flask_app.logger)
    syncd_books = ds.update_library(ebooks_dict, user)

    # check book needs updating
    key, data = syncd_books.items()[0]
    assert data['new'] is True, "wasn't stored on first sync"
    assert data['update'] is True, 'book should need update'
    assert 'ebook_id' in data, 'ebook_id should be present in ogreserver response'

    # set ebook_id in incoming data, same as ogreclient would
    ebooks_dict[ebooks_dict.keys()[0]]['ebook_id'] = data['ebook_id']

    # sync again
    syncd_books = ds.update_library(ebooks_dict, user)

    # assert book does not need update
    key, data = syncd_books.items()[0]
    assert data['update'] is False, 'book should not need update'


def test_sync_multiple_versions(flask_app, datastore, user):
    ebooks_dict = {
        u"Lewis\u0006Carroll\u0007Alice's Adventures in Wonderland": {
            'format': 'epub',
            'file_hash': 'd41d8cd98f00b204e9800998ecf8427e',
            'owner': 'mafro',
            'size': 139654
        },
    }

    # create the datastore and run a sync
    ds = DataStore(flask_app.config, flask_app.logger)
    syncd_books = ds.update_library(ebooks_dict, user)

    # extract ebook_id of syncd book
    ebook_id = syncd_books.itervalues().next()['ebook_id']

    assert datastore.db('test').table('versions').filter(
        {'ebook_id': ebook_id}
    ).count().run() == 1, 'should be 1 version'

    # same book author/title, different file hash
    ebooks_dict[ebooks_dict.keys()[0]]['file_hash'] = '058e92c024a88969b0875d5eaf18a0cd'

    # sync again
    ds.update_library(ebooks_dict, user)

    # assert only one ebook in DB
    assert datastore.db('test').table('ebooks').count().run() == 1, 'should only be 1 ebook'

    # assert ebook has two versions attached
    assert datastore.db('test').table('versions').filter(
        {'ebook_id': ebook_id}
    ).count().run() == 2, 'should be 2 versions'
