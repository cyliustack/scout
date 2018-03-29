#!/bin/bash

job="worker"
task_index_cmd="--task_index=$1"
if [[ "$1" = "2" ]]; then
    job="controller"
    task_index_cmd=""
fi

python ~/scout/t-bench/scripts/tf_cnn_benchmarks/tf_cnn_benchmarks.py \
    --local_parameter_device=gpu \
    --num_gpus=8 \
    --batch_size=64 --model=resnet50 --variable_update=distributed_all_reduce \
    --job_name=$job  \
    --worker_hosts=node0:50001,node1:50001 \
    --controller_host=controller0:50002 \
    --all_reduce_spec="pscpu" \
    --gpu_memory_frac_for_testing=0 \
    $task_index_cmd 
