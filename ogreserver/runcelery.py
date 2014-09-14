from __future__ import absolute_import

from .factory import create_app, make_celery
from .extensions.celery import register_tasks

app = create_app()
app.celery = make_celery(app)
register_tasks(app)

# simple reference for starting celery worker -app=runcelery:celery
celery = app.celery
