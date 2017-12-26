#!/bin/bash

BASE_DIR=$(dirname "$0")

if [[ "$1" == "" ]]; then 
	exit -1
else 
	model=$1
fi
if [[ "$model" == "seq2seq" ]]; then
	${BASE_DIR}/tfenv/seq2seq/bin/python nmt/scripts/wmt16_en_de.sh /tmp/wmt16 
 
elif [[ "$model" == "memnet" ]]; then
	${BASE_DIR}/tfenv/memnet/bin/python memnet/main.py --nhop 6 --mem_size 100 
fi 
