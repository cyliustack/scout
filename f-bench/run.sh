#!/bin/bash

BASE_DIR=$(dirname "$0")

if [[ "$1" == "" ]]; then 
	echo "usage: ./run.sh MODEL"
	exit -1
else 
	model=$1
fi
if [[ "$model" == "seq2seq" ]]; then
	${BASE_DIR}/tfenv/seq2seq/bin/python nmt/scripts/wmt16_en_de.sh /tmp/wmt16 
elif [[ "$model" == "memnet" ]]; then
	${BASE_DIR}/tfenv/memnet/bin/python memnet/main.py --nhop 6 --mem_size 100 
elif [[ "$model" == "deepq" ]]; then
	${BASE_DIR}/tfenv/deepq/python deepq/main.py --env_name=Breakout-v0 --is_train=True
elif [[ "$model" == "speech" ]]; then
    ${BASE_DIR}/tfenv/speech/python python -u DeepSpeech.py
	                                --train_files data/ldc93s1/ldc93s1.csv \
                                    --dev_files data/ldc93s1/ldc93s1.csv \
			                        --test_files data/ldc93s1/ldc93s1.csv \
									--train_batch_size 1 \
								    --dev_batch_size 1 \
									--test_batch_size 1 \
					                --n_hidden 494 \
					                --epoch 50 \
elif [[ "$model" == "autoenc" ]]; then
	${BASE_DIR}/tfenv/autoenc/python autoenc/run_main.py --dim_z 20
fi 
