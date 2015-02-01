from __future__ import absolute_import
from __future__ import unicode_literals

import os

from flask import current_app as app
from flask import render_template

import requests

from .extensions.database import setup_db_session

from .exceptions import ConversionFailedError, EbookNotFoundOnS3Error, S3DatastoreError, \
        AmazonItemNotAccessibleError
from .models.amazon import AmazonAPI
from .models.datastore import DataStore
from .models.goodreads import GoodreadsAPI


@app.celery.task
def query_ebook_metadata(ebook_data):
    """
    Set and validate ebook metadata, authors, title etc. by querying external APIs
    """
    with app.app_context():
        print ebook_data
        am_data = None

        am = AmazonAPI(
            app.config['AWS_ADVERTISING_API_ACCESS_KEY'],
            app.config['AWS_ADVERTISING_API_SECRET_KEY'],
            app.config['AWS_ADVERTISING_API_ASSOCIATE_TAG'],
        )

        try:
            # if have ASIN, query Amazon for exact author/title
            if 'asin' in ebook_data['meta'] and ebook_data['meta']['asin']:
                am_data = am.search(asin=ebook_data['meta']['asin'])
                print am_data
                # then query Amazon for ISBN
                from celery.contrib import rdb;rdb.set_trace()

        except AmazonItemNotAccessibleError:
            # Amazon won't tell us about this item; this is true for all Kindle ASIN's
            print 99
            pass

        if am_data is None:
            # search author, title on Amazon, return ISBN
            am_data = am.search(author=ebook_data['author'], title=ebook_data['title'])
            print 2
            print am_data

            # extract image URL from Amazon
            ebook_data['image_url'] = am_data['image_url']

            # then query Amazon for ISBN
            #ebook_data['isbn'] = isbn

        gr = GoodreadsAPI(app.config['GOODREADS_API_KEY'])

        if 'isbn' in ebook_data['meta'] and ebook_data['meta']['isbn']:
            # use ISBN to query Goodreads
            gr_data = gr.search(ebook_data['meta']['isbn'])
            print 3
            print gr_data

        else:
            gr_data = gr.search(author=am_data['author'], title=am_data['title'])
            print 4
            print gr_data

        # verify results with fuzzywuzzy compare

        # select/insert Author into authors table
        # update the ebook with FK to the author
        # update author field with GR's Author - Title (use first Author only)


@app.celery.task
def store_ebook(ebook_id, filename, file_hash, fmt, username):
    """
    Store an ebook in the datastore
    """
    with app.app_context():
        # initialise the DB connection in our fake app context
        setup_db_session(app)

        try:
            # create the datastore
            ds = DataStore(app.config, app.logger)

            # local path of uploaded file
            filepath = os.path.join(app.config['UPLOADED_EBOOKS_DEST'], os.path.basename(filename))

            # store the file into S3
            ds.store_ebook(ebook_id, file_hash, filepath, username)

        except S3DatastoreError as e:
            app.logger.error('Failed uploading {} with {}'.format(file_hash, e))

        finally:
            # always delete local files who share the same hash in their filename
            # (these are repeat uploads, uniquely named by Flask-Uploads)
            for fn in os.listdir(app.config['UPLOADED_EBOOKS_DEST']):
                if fn.startswith(file_hash):
                    os.remove(os.path.join(app.config['UPLOADED_EBOOKS_DEST'], fn))


@app.celery.task
def conversion_search():
    """
    Search for ebooks which are missing key formats epub & mobi
    """
    with app.app_context():
        # late import to prevent circular import
        from .models.conversion import Conversion
        conversion = Conversion(app.config, DataStore(app.config, app.logger), flask_app=app)
        conversion.search()


@app.celery.task(queue="conversion")
def convert(ebook_id, version_id, original_filename, dest_fmt):
    """
    Convert an ebook to other formats, currently mobi & epub
    """
    with app.app_context():
        # late import to prevent circular import
        from .models.conversion import Conversion
        conversion = Conversion(app.config, DataStore(app.config, app.logger), flask_app=app)

        try:
            conversion.convert(ebook_id, version_id, original_filename, dest_fmt)

        except EbookNotFoundOnS3Error:
            app.logger.warning('Book missing from S3 ({}, {}, {}, {})'.format(
                ebook_id, version_id, original_filename, dest_fmt
            ))
        except ConversionFailedError as e:
            app.logger.error('Conversion failed ({}, {}, {}, {})'.format(
                ebook_id, version_id, original_filename, dest_fmt
            ))
            app.logger.debug(e)


@app.celery.task
def send_mail(recipient, subject, template, **context):
    """
    Send an email via Mailgun

    curl -s --user 'api:YOUR_API_KEY' \
        https://api.mailgun.net/v2/YOUR_DOMAIN_NAME/messages \
        -F from='Excited User <YOU@YOUR_DOMAIN_NAME>' \
        -F to='foo@example.com' \
        -F subject='Hello' \
        -F text='Testing some Mailgun awesomness!' \
        --form-string html='<html>HTML version of the body</html>'
    """
    with app.app_context():
        domain = app.config['HOSTNAME']
        api_key = app.config['MAILGUN_API_KEY']
        sender = app.config['SECURITY_EMAIL_SENDER']

        parts = {}

        # render both the text & html templates for the mime message
        for part in ('txt', 'html'):
            parts[part] = render_template(
                'security/email/{}.{}'.format(template, part), **context
            )

        # send the email via Mailgun's API
        resp = requests.post(
            'https://api.mailgun.net/v2/{}/messages'.format(domain),
            auth=('api', api_key),
            data={
                'from': sender,
                'to': recipient,
                'subject': subject,
                'text': parts['txt'],
                'html': parts['html'],
            }
        )
        # celery logs on stdout
        print "'{}' email sent to {}, with id='{}'".format(
            subject,
            recipient,
            resp.json()['id']
        )


# TODO nightly which searches for duplicates by title
# calculate book title match score
#fuzz.token_set_ratio(string, '{} {}'.format(author, title))
