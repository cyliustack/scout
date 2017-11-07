#!/bin/bash
if [[ "$1" == "" ]] || [[ "$2" == "" ]] || [[ "$3" == "" ]] || [[ "$4" == "" ]] ; then 
	echo "Usage: ./start-worker.sh nid model batch_size num_gpus [options]"
	exit -1
else 
	nid=$1
	model=$2
	batch_size=$3
	num_gpus=$4
	python tf_cnn_benchmarks.py --local_parameter_device=cpu --num_gpus=${num_gpus} \
--batch_size=${batch_size} --model=${model} --variable_update=distributed_replicated \
--job_name=worker --ps_hosts=192.168.0.100:50000 \
--worker_hosts=192.168.0.101:50001 --task_index=${nid} 
fi
