include:
  - app.virtualenv
  - app.supervisor
  - calibre
  - closure-compiler
  - gunicorn
  - libsass
  - mysql
  - nodejs
  - pypiserver
  - rabbitmq
  - rabbitmq.celerybeat
  - rethinkdb


extend:
  gunicorn-config:
    file.managed:
      - context:
          worker_class: gevent
          gunicorn_port: {{ pillar['gunicorn_port'] }}

  app-virtualenv:
    virtualenv.managed:
      - requirements: /srv/{{ pillar['app_directory_name'] }}/ogreserver/config/requirements.txt
      - require:
        - pkg: pip-dependencies-extra

  ogreserver-supervisor-service:
    supervisord.running:
      - require:
        - cmd: rabbitmq-server-running
      - watch:
        - file: /etc/supervisor/conf.d/{{ pillar['app_name'] }}.conf
        - file: /etc/gunicorn.d/{{ pillar['app_name'] }}.conf.py

  pypiserver-log-dir:
    file.directory:
      - user: {{ pillar['app_user'] }}
      - group: {{ pillar['app_user'] }}

  pypiserver-supervisor-config:
    file.managed:
      - context:
          port: 8233
          runas: {{ pillar['app_user'] }}


# install bower.io for Foundation 5
bower:
  npm.installed:
    - require:
      - cmd: npm-install

bower-ogreserver-install:
  cmd.run:
    - name: bower install --config.interactive=false
    - cwd: /srv/{{ pillar['app_directory_name'] }}/ogreserver/static
    - user: {{ pillar['app_user'] }}
    - unless: test -d /srv/{{ pillar['app_directory_name'] }}/ogreserver/static/bower_components


/srv/{{ pillar['app_directory_name'] }}/ogreserver/static/stylesheets:
  file.directory:
    - user: {{ pillar['app_user'] }}
    - group: {{ pillar['app_user'] }}

# compile sass to css
sass-compile:
  cmd.run:
    - name: sassc -I bower_components/foundation/scss -I sass sass/app.scss stylesheets/app.css && sassc -I bower_components/foundation/scss -I sass sass/normalize.scss stylesheets/normalize.css
    - cwd: /srv/ogre/ogreserver/static
    - user: {{ pillar['app_user'] }}
    - unless: test -d /srv/{{ pillar['app_directory_name'] }}/ogreserver/static/stylesheets/app.css


pip-dependencies-extra:
  pkg.latest:
    - names:
      - libmysqlclient-dev
      - libevent-dev

flask-config-dir:
  file.directory:
    - name: /etc/{{ pillar['app_directory_name'] }}
    - user: {{ pillar['app_user'] }}
    - group: {{ pillar['app_user'] }}

flask-config:
  file.managed:
    - name: /etc/{{ pillar['app_directory_name'] }}/flask.app.conf.py
    - source: salt://ogreserver/flask.app.conf.py
    - template: jinja
    - user: {{ pillar['app_user'] }}
    - group: {{ pillar['app_user'] }}
    - require:
      - file: flask-config-dir
    - require_in:
      - service: supervisor

ogre-init:
  cmd.run:
    - name: /home/{{ pillar['app_user'] }}/.virtualenvs/{{ pillar['app_name'] }}/bin/python manage.py init_ogre
    - cwd: /srv/ogre
    - unless: /home/{{ pillar['app_user'] }}/.virtualenvs/{{ pillar['app_name'] }}/bin/python manage.py init_ogre --test
    - user: {{ pillar['app_user'] }}
    - require:
      - virtualenv: app-virtualenv
      - file: flask-config
      - mysql_grants: create-mysql-user-perms
      - pip: rethinkdb-python-driver
