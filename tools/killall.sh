#!/bin/bash
num_nodes=2 
for (( i=0 ; i<$num_nodes ; i++  ))
do
echo "Kill CUDA process on node"$i
	ssh node$i pkill python ;
    ssh node$i nvidia-smi 
done
