#!/bin/bash
# Install Required Python Packages
sudo pip install numpy scipy scikit-learn six pylint librosa h5py xlsxwriter pssh

# Install OpenCV: reference link -> https://docs.opencv.org/2.4/doc/tutorials/introduction/linux_install/linux_install.html
sudo apt-get install build-essential
sudo apt-get install cmake git libgtk2.0-dev pkg-config libavcodec-dev libavformat-dev libswscale-dev
sudo apt-get install python-dev python-numpy libtbb2 libtbb-dev libjpeg-dev libpng-dev libtiff-dev libjasper-dev libdc1394-22-dev
git clone https://github.com/opencv/opencv.git
cd ~/opencv
mkdir release
cd release
cmake -D CMAKE_BUILD_TYPE=RELEASE -D CMAKE_INSTALL_PREFIX=/usr/local ..
make -j
sudo make install


# Reqirements for using j-bench
wget "https://drive.google.com/uc?id=0Byvt-AfX75o1STUxZTFpMU10djA&export=download"

pushd ~/scout && git submodule init && git submodule update && pushd t-bench && git pull origin master  && popd
