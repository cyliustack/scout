#!/bin/bash 
mpirun -np 2 python horovod_keras_simple.py
rm checkpoint* 
