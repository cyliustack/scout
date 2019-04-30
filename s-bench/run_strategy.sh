#!/bin/bash 
C_NONE="\033[0;00m"
C_RED="\033[1;31m"
C_GREEN="\033[1;32m"
export TF_CONFIG='{"cluster": {"worker": ["localhost:5000" ], "ps": ["localhost:5001"]}, "task": {"type": "worker", "index": 0} }'

#export TF_CONFIG='{
#    "cluster": {
#        "worker": ["host1:port", "host2:port", "host3:port"],
#        "ps": ["host4:port", "host5:port"]
#    },
#   "task": {"type": "worker", "index": 1}
#}'
#

if [[ "$1" == "" ]]; then
    echo -e "${C_RED}Please specify the TensorFlow distribution strategy [mi|mw|ps|co]!${C_NONE}"
    exit 1
fi

strategy=$1
rm -rf mymodel
python ${strategy}.py mymodel
