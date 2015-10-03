#!/bin/bash -eux

SSH_USERNAME=${SSH_USERNAME:-vagrant}

if [[ $PACKER_BUILDER_TYPE =~ vmware ]]; then
    echo "==> Installing VMware Tools"
    apt-get install -y linux-headers-$(uname -r) build-essential perl git unzip

    cd /tmp
    git clone https://github.com/rasa/vmware-tools-patches.git
    cd vmware-tools-patches
    ./download-tools.sh 7.1.2
    ./untar-and-patch-and-compile.sh
fi
