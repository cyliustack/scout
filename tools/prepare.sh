#!/bin/bash
# Install Required Python Packages
WITH_SUDO=""
if [[ $(which sudo) ]]; then 
    WITH_SUDO="sudo" 
fi


#sudo pip install librosa  
# Install OpenCV: reference link -> https://docs.opencv.org/2.4/doc/tutorials/introduction/linux_install/linux_install.html
#sudo apt-get install build-essential
#sudo apt-get install cmake git libgtk2.0-dev pkg-config libavcodec-dev libavformat-dev libswscale-dev
#sudo apt-get install python-dev python-numpy libtbb2 libtbb-dev libjpeg-dev libpng-dev libtiff-dev libjasper-dev libdc1394-22-dev
#git clone https://github.com/opencv/opencv.git
#cd ~/opencv
#mkdir release
#cd release
#cmake -D CMAKE_BUILD_TYPE=RELEASE -D CMAKE_INSTALL_PREFIX=/usr/local ..
#make -j
#sudo make install

pip install --user numpy scipy scikit-learn six pylint xlsxwriter pssh h5py keras 

#OPENMPI=openmpi-3.1.3
#OPENMPI_TARBALL=openmpi-3.1.3.tar.bz2
#if [[ ! -f ${OPENMPI_TARBALL} ]]; then  
#   wget https://download.open-mpi.org/release/open-mpi/v3.1/${OPENMPI_TARBALL}
#fi
#if [[ ! -f /opt/${OPENMPI}/bin/mpicc ]]; then
#    tar xvf ${OPENMPI_TARBALL}
#    cd ${OPENMPI} && ./configure --prefix=/opt/${OPENMPI} && make -j && ${WITH_SUDO} make install && cd - 
#    rm ${OPENMPI_TARBALL}
#fi
#export PATH=$PATH:/opt/${OPENMPI}/bin 
#pip install --user horovod

# Reqirements for using j-bench
#wget "https://drive.google.com/uc?id=0Byvt-AfX75o1STUxZTFpMU10djA&export=download"

git submodule init
git submodule update
git submodule foreach git pull origin master
#cd p-bench && git pull & cd -
