#!/bin/bash
# Copyright (c) Jul. 2017, Cheng-Yueh Liu (cyliustack@gmail.com)

C_NONE="\033[0m"
C_CYAN="\033[36m"
C_RED="\033[31m"
C_GREEN="\033[32m"
C_ORANGE="\033[33m"
C_BLUE="\033[34m"
C_PURPLE="\033[35m"
C_CYAN="\033[36m"
C_LIGHT_GRAY="\033[37m"

print_misc() {
    echo -e "${C_PURPLE} $1 ${C_NONE}"
}

print_info() {
    echo -e "${C_BLUE} $1 ${C_NONE}"
}

print_error() {
    echo -e "${C_RED} $1 ${C_NONE}"
}

print_warning() {
    echo -e "${C_ORANGE} $1 ${C_NONE}"
}

#tf_cnn ${model} ${batch_size} ${num_gpus} ps $prefix_name $i ${ps_hosts} ${worker_hosts}
function tf_cnn(){
	model=$1
	batch_size=$2
	num_gpus=$3
	job_name=$4
	num_node=$5
	prefix_name=$5
	nid=$6
	ps_hosts=$7
	worker_hosts=$8

	host_name=$1$2
	ssh $1$2 echo "Run tf_cnn on ${host_name}" && \
	cd ~/benchmark/father/tf_cnn && \
	./node-info.sh hostname
	ps_hosts=hpc0:50000,hpc1:50000 
	worker_hosts=hpc0:50000,hpc1:50000 
	python tf_cnn_benchmarks.py --local_parameter_device=cpu --num_gpus=${num_gpus} \
	--batch_size=${batch_size} --model=resnet50 --variable_update=distributed_replicated \
	--job_name=${job_name} --ps_hosts=${ps_hosts}\
	--worker_hosts=${worker_hosts} --task_index=${nid}
	#--data_dir=/mnt/dataset/imagenet
}



if [[ "$1" == "" ]] || [[ "$2" == "" ]] || [[ "$3" == "" ]] || [[ "$4" == "" ]] || [[ "$5" == "" ]] ; then 
	echo "Usage: ./dist-train.sh model batch_size num_gpus num_node prefix_name [options]"
	exit -1
else 
	model=$1
	batch_size=$2
	num_gpus=$3
	num_node=$4
	prefix_name=$5
	ps_hosts=""
	worker_hosts=""
	for (( i=0 ; i<${num_node} ; i++ ))	
	do
		ps_hosts+="$prefix_name$i:50000," 
		worker_hosts+="$prefix_name$i:50001," 
	done


	for (( i=0 ; i<${num_node} ; i++ ))	
	do
		tf_cnn ${model} ${batch_size} ${num_gpus} ps $prefix_name $i ${ps_hosts} ${worker_hosts}
	done
	
	for (( i=0 ; i<${num_node} ; i++ ))	
	do
		tf_cnn ${model} ${batch_size} ${num_gpus} worker $prefix_name $i ${ps_hosts} ${worker_hosts}
	done


	#pssh -PH "$hosts" hostname

	if [[ "$(hostname)" == "${prefix_name}0" ]] ; then 
		echo "This is Node-$( hostname | sed 's/${prefix_name}//g') "
	 	echo "Act as a parameter server." && exit 0
	else 
		echo "This is Node-$(hostname | sed 's/${prefix_name}//g') "
		echo "Act as a worker." && exit 0
	fi
fi	

#if [ "$(hostname)" == "${prefix_name}0" ] ; then 
# echo "This is Node-$( hostname | sed 's/hpc//g') "
# echo "Act as a parameter server." && exit 0
#python trainer.py \
#    --ps_hosts=hpc0:2222 \
#    --worker_hosts=hpc1:2222,hpc2:2222,hpc3:2222 \
#    --job_name=ps --task_index=0
#else 
#    echo "This is Node-$(hostname | sed 's/hpc//g') "
#    echo "Act as a worker." && exit 0
#    python trainer.py \
#    --ps_hosts=hpc0:2222 \
#    --worker_hosts=hpc1:2222,hpc2:2222,hpc3:2222 \
#    --job_name=worker --task_index=$( hostname | sed 's/hpc//g')
#fi 
