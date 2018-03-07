#!/bin/bash
ps_port=$(shuf -i 50000-57999 -n 1)
model=inception3
ps_servers=""
wk_servers=""
num_nodes=2
num_workers_per_node=2
gpu_memory_frac_for_testing=0.3 
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
max_steps=60
batch_size=32
models_dir=~/scout/t-bench/scripts/tf_cnn_benchmarks
#models_dir=~/tensorflow-models/research/inception
#models_dir=~/workspace/models/research/inception
#with_env="source ~/setenv.sh && source ~/tf-nightly/bin/activate "
with_env="source ~/setenv.sh "
#exit 0


for (( i=0; i<$num_nodes; i++ ))
do 
	nid=$i
	for (( k=0; k<$num_workers_per_node; k++ ))
	do
		wid=`expr $i \* $num_workers_per_node + $k` 
		echo "Lauch worker-${wid} on Node$i"
		ssh node$nid \
		"${with_env} && cd ${models_dir} &&  \
		python tf_cnn_benchmarks.py \
		--model=${model} \
		--batch_size=${batch_size} \
		--data_name=imagenet \
		--data_dir=$HOME/ImageNetData/ImageNet_TFRecord \
		--job_name='worker' \
		--task_index=${wid} \
		--gpu_memory_frac_for_testing=${gpu_memory_frac_for_testing} \
		--ps_hosts=${ps_servers} \
		--train_dir=/tmp/imagenet_train \
		--server_protocol=grpc \
		--num_batches=${max_steps} \
		--worker_hosts=${wk_servers} \
		2> /dev/null" &
	done

	echo "Lauch PS on Node"$nid
	ssh node$nid hostname 	
	ssh node$nid rm -r /tmp/imagenet_train
	ssh node$nid \
	"${with_env} && cd ${models_dir} && \
	python tf_cnn_benchmarks.py \
	--model=${model} \
	--batch_size=${batch_size} \
	--data_name=imagenet \
	--data_dir=$HOME/ImageNetData/ImageNet_TFRecord \
	--job_name='ps' \
	--task_index=$nid \
	--gpu_memory_frac_for_testing=${gpu_memory_frac_for_testing} \
	--ps_hosts=${ps_servers} \
	--train_dir=/tmp/imagenet_train \
	--server_protocol=grpc \
	--num_batches=${max_steps} \
	--worker_hosts=${wk_servers} \
	2> /dev/null" &
done


