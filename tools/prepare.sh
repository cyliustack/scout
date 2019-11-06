#!/bin/bash
# Install Required Python Packages
WITH_SUDO=""
if [[ $(which sudo) ]]; then 
    WITH_SUDO="sudo" 
fi

FLAG_PIP=""
if [[ "${VIRTUAL_ENV}" == "" ]]; then
    echo "pip uses --user"
    FLAG_PIP += "--user"
fi

python -m pip install pandas numpy scipy scikit-learn six pylint xlsxwriter pssh h5py keras ${FLAG_PIP} efficientnet jupyter jupyterlab scikit-image opencv-python 

git clone https://github.com/tensorflow/benchmarks
cd benchmarks && git checkout cnn_tf_v1.13_compatible && cd -
rm -rf pytorch_examples/.git/ && rm -rf pytorch_examples
git clone https://github.com/pytorch/examples
mv examples pytorch_examples
