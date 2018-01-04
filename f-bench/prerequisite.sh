#!/bin/bash

BASE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"

if [ -f /etc/os-release ]; then
    # freedesktop.org and systemd
    . /etc/os-release
    OS=$NAME
    VER=$VERSION_ID
elif type lsb_release >/dev/null 2>&1; then
    # linuxbase.org
    OS=$(lsb_release -si)
    VER=$(lsb_release -sr)
elif [ -f /etc/lsb-release ]; then
    # For some versions of Debian/Ubuntu without lsb_release command
    . /etc/lsb-release
    OS=$DISTRIB_ID
    VER=$DISTRIB_RELEASE
elif [ -f /etc/debian_version ]; then
    # Older Debian/Ubuntu/etc.
    OS=Debian
    VER=$(cat /etc/debian_version)
elif [ -f /etc/SuSe-release ]; then
    # Older SuSE/etc.
    ...
elif [ -f /etc/redhat-release ]; then
    # Older Red Hat, CentOS, etc.
    ...
else
    # Fall back to uname, e.g. "Linux <version>", also works for BSD, etc.
    OS=$(uname -s)
    VER=$(uname -r)
fi


echo $OS
echo $ARCH
echo $VERSION

os_found=true

if [[ $OS == "Ubuntu" ]]; then
	echo "This is Ubuntu "
	sudo apt-get install libboost-dev libpcap-dev libconfig-dev libconfig++-dev linux-tools-common linux-tools-$(uname -r) linux-cloud-tools-$(uname -r)  linux-tools-generic linux-cloud-tools-generic cmake python-pip python-dev	python3-tk
elif [[ $OS == "CentOS Linux" ]]; then
    echo "This is CentOS"
    sudo yum install perf cmake libpcap-devel libconfig-devel boost-devel install centos-release-scl devtoolset-4-gcc* python-pip python-devel libxml2-dev libxslt-dev tkinter
elif [[ $OS == "Fedora" ]]; then
	echo "This Fedora "
    sudo dnf -y install perf boost-devel libconfig-devel libpcap-devel cmake python-pip python-devel python3-tkinter
else
	os_found=false
fi

if [[ $os_found == true ]]; then
    wget http://bitbucket.org/eigen/eigen/get/3.3.4.tar.gz
	tar -xvf 3.3.4.tar.gz && cd eigen-eigen-5a0156e40feb && mkdir -p build && cd build && cmake .. && make && sudo make install 
    cd ../.. 
    rm 3.3.4.tar.gz
    rm -rf eigen-eigen-5a0156e40feb
else
   echo "Oops, Cannot identify your OS version!"
fi
sudo pip install --upgrade pip
sudo pip install cxxfilt scapy pandas 
sudo pip install virtualenv

mkdir -p "${BASE_DIR}/tfenv"
mkdir -p "${BASE_DIR}/tfenv/seq2seq"
mkdir -p "${BASE_DIR}/tfenv/memnet"
mkdir -p "${BASE_DIR}/tfenv/deepq"
mkdir -p "${BASE_DIR}/tfenv/autoenc"
mkdir -p "${BASE_DIR}/tfenv/speech"
virtualenv -q "${BASE_DIR}/tfenv/seq2seq"
virtualenv -q "${BASE_DIR}/tfenv/memnet"
virtualenv -q "${BASE_DIR}/tfenv/deepq"
virtualenv -q "${BASE_DIR}/tfenv/autoenc"
virtualenv -q "${BASE_DIR}/tfenv/speech"
${BASE_DIR}/tfenv/seq2seq/bin/pip install -U pip
${BASE_DIR}/tfenv/seq2seq/bin/pip install -r requirement/seq2seq-requirement.txt
${BASE_DIR}/tfenv/memnet/bin/pip install -U pip
${BASE_DIR}/tfenv/memnet/bin/pip install -r requirement/memnet-requirement.txt
${BASE_DIR}/tfenv/deepq/bin/pip install -U pip
${BASE_DIR}/tfenv/deepq/bin/pip install -r requirement/deepq-requirement.txt
${BASE_DIR}/tfenv/autoenc/bin/pip install -U pip
${BASE_DIR}/tfenv/autoenc/bin/pip install -r requirement/autoenc-requirement.txt
${BASE_DIR}/tfenv/speech/bin/pip install -U pip
${BASE_DIR}/tfenv/speech/bin/pip install -r requirement/speech-requirement.txt
python ${BASE_DIR}/speech/util/taskcluster.py --target ./native-client --arch gpu 
