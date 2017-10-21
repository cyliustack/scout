#!/bin/bash
if [[ "$1" == "" ]] || [[ "$2" == "" ]] || [[ "$3" == "" ]] ; then 
	echo "Usage: ./avx-train.sh model batch_size num_threads [options]"
	exit -1
else 
	model=$1
	batch_size=$2
	num_intra_threads=$3
    python tf_cnn_benchmarks.py --local_parameter_device=cpu --num_gpus=1 --num_inter_threads=1 --num_intra_threads=${num_intra_threads} --batch_size=${batch_size} --model=${model} --variable_update=parameter_server --use_nccl=False --device=cpu --data_format=NHWC --num_batches=10 $4
#--data_dir=dd/mnt/dataset/imagenet
fi 
