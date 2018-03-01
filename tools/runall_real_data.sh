#!/bin/bash
ps_port=$(shuf -i 50000-65535 -n 1)
wk_port=$(shuf -i 58000-65535 -n 1)
ps_servers=""
wk_servers=""
base_node=0
num_nodes=2
for (( i=$base_node ; i < $num_nodes ; i++ ))
do
	if [[ $i == $base_node ]]; then
		ps_servers=node$base_node:$ps_port
		wk_servers=node$base_node:$wk_port
	else
		ps_servers=$ps_servers,node$i:$ps_port
		wk_servers=$wk_servers,node$i:$wk_port
	fi
done

echo "PS SERVERS: "$ps_servers
echo "WK_SERVERS: "$wk_servers

for (( i=$base_node; i<$num_nodes; i++ ))
do 
	echo "Lauch Node $i"
	ssh node$i \
	cd $HOME/tensorflow-models/research/inception &&  \
	bazel-bin/inception/imagenet_distributed_train \
	--batch_size=16 \
	--data_dir=$HOME/ImageNetData/ImageNet_TFRecord \
	--job_name='worker' \
	--task_id=$i \
	--per_process_gpu_memory_fraction=0.45 \
	--ps_hosts=$ps_servers \
	--worker_hosts=$wk_servers &
	
	ssh node$i \
	cd $HOME/tensorflow-models/research/inception &&  \
	bazel-bin/inception/imagenet_distributed_train \
	--batch_size=16 \
	--data_dir=$HOME/ImageNetData/ImageNet_TFRecord \
	--job_name='ps' \
	--task_id=$i \
	--per_process_gpu_memory_fraction=0.45 \
	--ps_hosts=$ps_servers \
	--worker_hosts=$wk_servers &
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
