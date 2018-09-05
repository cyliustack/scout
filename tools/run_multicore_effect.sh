#!/bin/bash 
LOG_FILE=multicore_effect.log
arr[0]=0xffffffffffffffff 
arr[1]=0xffffffff 
arr[2]=0xffff 
arr[3]=0xff 
arr[4]=0xf
arr[5]=0x3
arr[6]=0x1
echo "" > ${LOG_FILE}
for i in {0..6};
do
    echo ${i}' = '${arr[$i]} 1>> ${LOG_FILE}
    python tf_cnn_benchmarks.py --model=resnet50 --batch_size=64 --num_gpus=16 --variable_update=replicated --local_parameter_device=gpu --train_dir=/tmp/mytrain --data_dir=/tmp/ramdisk/dataset/imagenet --all_reduce_spec=nccl  1>> ${LOG_FILE}  & sleep 3 && ps aux | grep tf_cnn_benchmarks | head -n 1 | awk {'print $2'} | xargs taskset -p ${arr[$i]} 
    wait
    echo "all processes done for "$i"-th run!" 
done
