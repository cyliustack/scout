#!/bin/bash 
LOG_FILE=multicore_effect.log
arr[0]=0x1 
arr[1]=0x3 
arr[2]=0xf 
arr[3]=0xff 
arr[4]=0xffff
arr[5]=0xffffffff 
arr[6]=0xffffffffffff 
echo "" > ${LOG_FILE}
for i in {6..6};
do
    echo ${i}' = '${arr[$i]} 1>> ${LOG_FILE}
    ./scout t-bench resnet50 --num_batches=100 --num_gpus=16 1>> ${LOG_FILE}  & sleep 3 && ps aux | grep tf_cnn_benchmarks | head -n 1 | awk {'print $2'} | xargs taskset -p ${arr[$i]} 
    wait
    echo "all processes done for "$i"-th run!" 
done
