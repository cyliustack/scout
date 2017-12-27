#!/bin/bash
if [[ "$1" == "" ]] || [[ "$2" == "" ]] || [[ "$3" == "" ]]; then 
	echo "Usage: ./upload-logs.sh ip_address username list_of_log_files"
	exit -1
else 
    ip_address=$1
    username=$2
    shift
    shift
    scp $*  ${username}@${ip_address}:~
fi 
