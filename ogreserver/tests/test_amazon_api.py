from __future__ import absolute_import
from __future__ import unicode_literals

from ..exceptions import AmazonItemNotAccessibleError

import pytest


def test_kindle_asin_lookup_failure(amazon):
    with pytest.raises(AmazonItemNotAccessibleError):
        amazon.search(asin='eggsbacon')


def test_author_title_search(amazon):
    # search author, title on Amazon
    am_data = amazon.search(author='Max Brooks', title='World War Z')

    assert am_data['asin'] == 'B000JMKQX0'
    assert am_data['title'] == 'World War Z: An Oral History of the Zombie War'
    assert am_data['image_url'] == 'http://ecx.images-amazon.com/images/I/51ELXqAe9UL.jpg'
    assert am_data['author'] == 'Max Brooks'

    am_data = amazon.search(author='Richard Morgan', title='Altered Carbon (GOLLANCZ S.F.)')
    import ipdb;ipdb.set_trace()


def test_query_ebook_metadata
