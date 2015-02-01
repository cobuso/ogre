from __future__ import absolute_import
from __future__ import unicode_literals


def test_isbn_search(goodreads):
    # search ISBN on goodreads
    gr_data = goodreads.search('0307346609')
    assert gr_data['isbn'] == '0307346609'
    assert gr_data['isbn13'] == '9780307346605'
    assert gr_data['title'] == 'World War Z: An Oral History of the Zombie War'
    assert len(gr_data['authors']) == 1
    assert gr_data['authors'][0]['name'] == 'Max Brooks'


def test_isbn13_search(goodreads):
    # search ISBN13 on goodreads
    gr_data = goodreads.search('9780307346605')
    assert gr_data['isbn'] == '0307346609'
    assert gr_data['isbn13'] == '9780307346605'
    assert gr_data['title'] == 'World War Z: An Oral History of the Zombie War'
    assert len(gr_data['authors']) == 1
    assert gr_data['authors'][0]['name'] == 'Max Brooks'


def test_author_title_search(goodreads):
    # search author, title on goodreads
    gr_data = goodreads.search(author='Richard Morgan', title='Altered Carbon (GOLLANCZ S.F.)')

    import ipdb;ipdb.set_trace()
    # assert image URL
    #assert 'image_url' in am_data
    #assert len(am_data['image_url']) != 0
