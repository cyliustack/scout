#!/bin/bash
num_nodes=2 
for (( i=0 ; i<$num_nodes ; i++  ))
do
	echo "Kill CUDA process on node"$i
	ssh node$i "~/scout/tools/killby sofa;"
	ssh node$i "~/scout/tools/killby scout;"
	ssh node$i "~/scout/tools/killby tf; sleep 1 &&  nvidia-smi"
done
