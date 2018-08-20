#!/usr/bin/env python3
import subprocess
import os
from pathlib import Path

if __name__ == '__main__':
    mypath = os.getcwd()
    print(mypath)
    with open(mypath + '/multicore-effect.log','w') as f:
        subprocess.call('echo SCOUT_TOOL', shell=True, stdout=f)   
    with open(mypath + '/multicore-effect.log','a') as f:
        for i in range(0,6):
            p1 = subprocess.Popen('echo ' + str(i), shell=True, stdout=f)
            p2 = subprocess.Popen( mypath + '/scout t-bench resnet50 --num_batches=100 --num_gpus=16 1>> ${LOG_FILE}  & sleep 3 && ps aux | grep tf_cnn_benchmarks | head -n 1 | awk {"print $2"} | xargs taskset -p ${arr[$i]}', shell=True, stdout=f)
            p2.wait()
     
