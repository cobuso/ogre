#!/bin/bash -eux

GIT_REVISION=${GIT_REVISION:-master}

mkdir /etc/ogreserver
cd /etc/ogreserver || exit 2

echo 'Created /etc/ogreserver'
echo "Retrieving prod_vars.sesame from oii/ogre at ${GIT_REVISION}"

curl --silent -o /tmp/sesame.sh https://raw.githubusercontent.com/mafrosis/sesame.sh/master/sesame.sh &>/dev/null
chmod +x /tmp/sesame.sh

# fetch default_vars
curl --silent -o /etc/ogreserver/default_vars.sls "https://raw.githubusercontent.com/oii/ogre/${GIT_REVISION}/ogreserver/config/pillar/default_vars.sls"

# fetch encrypted prod_vars
curl --silent -o /tmp/prod_vars.sesame "https://raw.githubusercontent.com/oii/ogre/${GIT_REVISION}/ogreserver/config/pillar/prod_vars.sesame"

if [[ $? -gt 0 ]]; then
	echo 'Encrypted pillar not found on Github'
	exit 1
fi

/tmp/sesame.sh d -p "${SESAME_PASSWORD}" /tmp/prod_vars.sesame

# make pillar readable by salt
chown -R root:root /etc/ogreserver
chmod 640 /etc/ogreserver/*

if [[ -f /etc/ogreserver/prod_vars.sls ]]; then
	echo 'Decrypted prod_vars pillar into /etc/ogreserver'
fi
