#!/bin/bash
if [[ "$1" == "" ]] || [[ "$2" == "" ]] || [[ "$3" == "" ]] || [[ "$4" == "" ]] ; then 
	echo "Usage: ./batch_run.sh model bsBegin bsEnd numGPUs [options]"
	exit -1
else
	model=$1
	bs_begin=$2
	bs_end=$3
	num_gpus=$4
	options=$5

	if [[ ${model} == "vgg16" || ${model} == "vgg19" ]] ; then
		options=${options}" --local_parameter_device=gpu  --variable_update=replicated  --use_nccl=True "
	fi
	echo $options
	logfile=${model}_GPUx${num_gpus}_batches.log
	echo " " >  ${logfile}
	for (( bs=${bs_begin}; bs<=${bs_end}; bs*=2 ))
	do  
		echo "Run ${modle} on GPUx${num_gpus} with batch-size ${bs} : "
		./tools/gpu-train.sh	${model}	${bs}	${num_gpus}	"${options}"	1>> ${logfile}
	done
	cat ${logfile} | grep "total images/sec:" |  awk '{ print $3; print ","; }'  | xargs
fi
