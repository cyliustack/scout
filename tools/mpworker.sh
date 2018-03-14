#!/bin/bash
ps_port=$(shuf -i 50000-57999 -n 1)
model=inception3
ps_servers=""
wk_servers=""
num_nodes=2
num_workers_per_node=2
gpu_memory_frac_for_testing=0.0 
protocol="grpc+verbs"
debug="2> /dev/null"
for (( i=0 ; i < $num_nodes ; i++ ))
do
	if [[ $i == 0 ]]; then
		ps_servers=node$i:$ps_port
	else
		ps_servers=$ps_servers,node$i:$ps_port
	fi


	for (( k=0 ; k < $num_workers_per_node ; k++ ))
	do
		wk_port=$(shuf -i 58000-65535 -n 1)
		echo "worker: "node$i:$wk_port
		if [[ $wk_servers != "" ]]; then
			wk_servers=$wk_servers,
		fi
		wk_servers=$wk_servers"node$i:${wk_port}"
	done
done
echo "PS SERVERS: "$ps_servers
echo "WK_SERVERS: "$wk_servers
max_steps=10
#max_steps=6000000
batch_size=64
models_dir=~/scout/t-bench/scripts/tf_cnn_benchmarks
#models_dir=~/tensorflow-models/research/inception
#models_dir=~/workspace/models/research/inception
data_dir=/tmp/ImageNetData/ImageNet_TFRecord
#data_dir=$HOME/ImageNetData/ImageNet_TFRecord
#with_env="source ~/setenv.sh && source ~/tf-nightly/bin/activate "
with_env="source ~/setenv.sh && source ~/apps/sofa/tools/activate.sh "
profile_begin=""
profile_end=""
#exit 0


for (( i=0; i<$num_nodes; i++ ))
do 
	nid=$i
	for (( k=0; k<$num_workers_per_node; k++ ))
	do
		wid=`expr $i \* $num_workers_per_node + $k`   
		echo "Lauch worker-${wid} on Node$i"

		if [[ "${nid}" = "0" ]] && [[ "${wid}" == "0" ]] ; then
			echo "Apply SOFA for ${nid}:${wid}"
			profile_begin="sofa record '"
			profile_end="'"
		else
			profile_begin=" "
			profile_end=" "
		fi

		ssh node$nid \
		"${with_env} && cd ${models_dir} && \
		CUDA_VISIBLE_DEVICES=$k ${profile_begin} python tf_cnn_benchmarks.py \
		--model=${model} \
		--batch_size=${batch_size} \
		--variable_update=parameter_server \
		--local_parameter_device=cpu \
		--num_gpus=1 \
		--data_name=imagenet \
		--data_dir=${data_dir} \
		--job_name='worker' \
		--task_index=${wid} \
		--gpu_memory_frac_for_testing=${gpu_memory_frac_for_testing} \
		--ps_hosts=${ps_servers} \
		--train_dir=/tmp/imagenet_train \
		--server_protocol=${protocol} \
		--num_batches=${max_steps} \
		--worker_hosts=${wk_servers} \
		${debug} ${profile_end}" &
	done

	echo "Lauch PS on Node"$nid
	ssh node$nid hostname 	
	ssh node$nid rm -r /tmp/imagenet_train
	ssh node$nid \
	"${with_env} && cd ${models_dir} && \
 	CUDA_VISIBLE_DEVICES=-1 python tf_cnn_benchmarks.py \
	--model=${model} \
	--batch_size=${batch_size} \
	--local_parameter_device=cpu \
	--variable_update=parameter_server \
	--num_gpus=1 \
	--data_name=imagenet \
	--data_dir=${data_dir} \
	--job_name='ps' \
	--task_index=$nid \
	--gpu_memory_frac_for_testing=${gpu_memory_frac_for_testing} \
	--ps_hosts=${ps_servers} \
	--train_dir=/tmp/imagenet_train \
	--server_protocol=${protocol} \
	--num_batches=${max_steps} \
	--worker_hosts=${wk_servers} \
	${debug} " &
done
sleep 120 && ./killall.sh


