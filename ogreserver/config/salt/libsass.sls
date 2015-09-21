libsass-src:
  git.latest:
    - name: https://github.com/sass/libsass.git
    - target: /tmp/libsass

sassc-src:
  git.latest:
    - name: https://github.com/sass/sassc.git
    - target: /tmp/sassc

sassc-make:
  cmd.run:
    - name: SASS_LIBSASS_PATH=/tmp/libsass make
    - cwd: /tmp/sassc
    - unless: test -f /tmp/sassc/bin/sassc
    - require:
      - git: libsass-src
      - git: sassc-src

sassc-install:
  cmd.run:
    - name: cp /tmp/sassc/bin/sassc /usr/local/bin/sassc && chmod 755 /usr/local/bin/sassc
    - unless: test -f /usr/local/bin/sassc
    - require:
      - cmd: sassc-make
