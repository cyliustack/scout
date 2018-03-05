#!/bin/bash
ps_port=$(shuf -i 50000-65535 -n 1)
wk_port=$(shuf -i 58000-65535 -n 1)
ps_servers=""
wk_servers=""
first_node=1
last_node=1
num_nodes=`expr $last_node - $first_node + 1`
for (( i=$first_node ; i <= $last_node ; i++ ))
do
	if [[ $i == $first_node ]]; then
		ps_servers=node$first_node:$ps_port
		wk_servers=node$first_node:$wk_port
	else
		ps_servers=$ps_servers,node$i:$ps_port
		wk_servers=$wk_servers,node$i:$wk_port
	fi
done

echo "PS SERVERS: "$ps_servers
echo "WK_SERVERS: "$wk_servers

for (( i=0; i<$num_nodes; i++ ))
do 
	nid=$( expr $i + $first_node )
	echo "Lauch Node"$nid
	ssh node$nid hostname 	

	ssh node$nid \
	"cd tensorflow-models/research/inception &&  \
	bazel-bin/inception/imagenet_distributed_train \
	--input_queue_memory_factor=4 \
	--batch_size=16 \
	--data_dir=$HOME/ImageNetData/ImageNet_TFRecord \
	--job_name='worker' \
	--task_id=$i \
	--ps_hosts=$ps_servers \
	--train_dir=/tmp/imagenet_train \
	--worker_hosts=$wk_servers" &

	
	ssh node$nid \
	"cd tensorflow-models/research/inception &&  \
	bazel-bin/inception/imagenet_distributed_train \
	--input_queue_memory_factor=4 \
	--batch_size=16 \
	--data_dir=$HOME/ImageNetData/ImageNet_TFRecord \
	--job_name='ps' \
	--task_id=$i \
	--ps_hosts=$ps_servers \
	--train_dir=/tmp/imagenet_train \
	--worker_hosts=$wk_servers" &
done




#ssh node0 \
#cd ~/tensorflow-models/research/inception &&  \
#bazel-bin/inception/imagenet_distributed_train \
#--batch_size=32 \
#--data_dir=$HOME/ImageNetData/ImageNet_TFRecord \
#--job_name='ps' \
#--task_id=0 \
#--per_process_gpu_memory_fraction=0.45 \
#--ps_hosts='node0:${ps_port},node1:${ps_port}' \
#--worker_hosts='node0:${worker_port},node1:${worker_port}' &
#--ps_hosts="node0:${ps_port},node1:${ps_port}" \
#--worker_hosts="node0:${worker_port},node1:${worker_port}" &
#
#
#ssh node1 \
#cd ~/tensorflow-models/research/inception &&  \
#bazel-bin/inception/imagenet_distributed_train \
#--batch_size=32 \
#--data_dir=$HOME/ImageNetData/ImageNet_TFRecord \
#--job_name='worker' \
#--task_id=1 \
#--per_process_gpu_memory_fraction=0.45 \
#--ps_hosts='node0:${ps_port},node1:${ps_port}' \
#--worker_hosts='node0:${worker_port},node1:${worker_port}' &
#--ps_hosts="node0:${ps_port},node1:${ps_port}" \
#--worker_hosts="node0:${worker_port},node1:${worker_port}" &
#
#
#
#ssh node1 \
#cd ~/tensorflow-models/research/inception &&  \
#bazel-bin/inception/imagenet_distributed_train \
#--batch_size=32 \
#--data_dir=$HOME/ImageNetData/ImageNet_TFRecord \
#--job_name='ps' \
#--task_id=1 \
#--per_process_gpu_memory_fraction=0.45 \
#--ps_hosts='node0:${ps_port},node1:${ps_port}' \
#--worker_hosts='node0:${worker_port},node1:${worker_port}' &
#--ps_hosts="node0:${ps_port},node1:${ps_port}" \
#--worker_hosts="node0:${worker_port},node1:${worker_port}" &
#
#
