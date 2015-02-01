from __future__ import absolute_import
from __future__ import unicode_literals

import bottlenose
import xml.etree.cElementTree as ET

from ..exceptions import AmazonAPIError, AmazonItemNotAccessibleError, \
        AmazonNoMatchesError


class AmazonAPI:
    NS = 'http://webservices.amazon.com/AWSECommerceService/2011-08-01'

    def __init__(self, access_key, secret_key, associate_tag):
        self.amazon = bottlenose.Amazon(
            access_key,
            secret_key,
            associate_tag,
            MaxQPS=0.9
        )


    def _preprocess(self, xml, debug=False):
        """
        Helper function to get to the good stuff in response from Amazon API
        """
        if debug:
            print xml

        tree = ET.fromstring(xml)
        items = tree.find('{{{}}}Items'.format(self.NS))

        # handle errors from the API call
        errors = items.find('{{{}}}Request'.format(self.NS)).find(
            '{{{}}}Errors'.format(self.NS)
        )

        if errors is not None and len(errors.getchildren()) > 0:
            # check request was valid
            request_is_valid = items.find('{{{}}}Request'.format(self.NS)).find(
                '{{{}}}IsValid'.format(self.NS)
            ).text

            if request_is_valid == 'False':
                # extract the error message and raise generic exception
                message = errors.find('{{{}}}Error'.format(self.NS)).find(
                    '{{{}}}Message'.format(self.NS)
                ).text

                raise AmazonAPIError(message)
            else:
                # get the error message code and raise specific exception
                code = errors.find('{{{}}}Error'.format(self.NS)).find(
                    '{{{}}}Code'.format(self.NS)
                ).text

                if code == 'AWS.ECommerceService.ItemNotAccessible':
                    raise AmazonItemNotAccessibleError
                elif code == 'AWS.ECommerceService.NoExactMatches':
                    raise AmazonNoMatchesError

        # return the Item object
        return items.find('{{{}}}Item'.format(self.NS))


    def search(self, author=None, title=None, asin=None):
        if asin is not None:
            xml = self.amazon.ItemLookup(ItemId=asin)
        else:
            xml = self.amazon.ItemSearch(
                Keywords='{} {}'.format(author, title),
                SearchIndex='KindleStore'
            )

        if str('isbn') in xml or str('ISBN') in xml:
            from celery.contrib import rdb;rdb.set_trace()
            egg = 'found isbn in amazon response'

        item = self._preprocess(xml, debug=True)

        output = {}

        # extract the interesting bits
        if asin is None:
            output['asin'] = item.find('{{{}}}ASIN'.format(self.NS)).text
        else:
            output['asin'] = asin

        # further interesting bits
        item = item.find('{{{}}}ItemAttributes'.format(self.NS))
        output['author'] = item.find('{{{}}}Author'.format(self.NS)).text
        output['title'] = item.find('{{{}}}Title'.format(self.NS)).text

        # query for an image
        xml = self.amazon.ItemLookup(
            ItemId=output['asin'],
            ResponseGroup='Images'
        )
        item = self._preprocess(xml)

        # extract a book cover URL
        output['image_url'] = item.find(
            '{{{}}}LargeImage'.format(self.NS)
        ).find(
            '{{{}}}URL'.format(self.NS)
        ).text

        return output
