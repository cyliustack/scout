#!/bin/bash
num_nodes=2 
for (( i=0 ; i<$num_nodes ; i++  ))
do
echo "Kill python on node"$i
	ssh node$i pkill python ; 
done
