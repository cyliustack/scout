#!/usr/bin/python 
import os 
import subprocess
from scapy.all import *
import sqlite3
import pandas as pd
import numpy as np
import csv
import json
import sys
import argparse
import multiprocessing as mp 
import glob, os 
from functools import partial


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Xring Modeling')
    parser.add_argument('--logdir', metavar="/path/to/logdir/", type=str, required=False, 
                    help='path to the directory of profiling log files')
    parser.add_argument('--max_num_gpus', metavar="N", type=int, required=False,
                    help='specify maximum number of GPUs to model')
    parser.add_argument('--metric', type=str, required=False, metavar='metric',
                    help='performance metric, like hotspot, memory pressure')
    parser.add_argument('command', type=str, nargs=1, metavar='command',
            help='specify a command: [record|report]')
 
    logfile = 'xring-report.txt' 
    args = parser.parse_args()
    command = args.command[0]

    if command == 'record':
        os.system("echo XRING TEST > "+logfile)  
        for i in range(1,8):
            print("Test xring for GPUx%d" % (i+1) )
            os.system("sofa stat  python tf_cnn_benchmarks.py --model=vgg16 --batch_size=64 --variable_update=replicated --num_gpus=%d --local_parameter_device=gpu --num_batches=10 --all_reduce_spec=xring 1>> %s " % ( i+1, logfile ) )
        
    if command == 'report':
        traffics = []
        with open(logfile) as f:
            lines = f.readlines()
            n_gpus = 0
            for line in lines:
                if line.find("MeasuredTotalTraffic") != -1 :
                    traffic = int(float(line.split()[2])) 
                    n_gpus = n_gpus + 1
                    print("GPUx%d : %d" % ( n_gpus, traffic) )
                    traffics.append(traffic)
        with open("xring.csv", "w") as outcsv:
            writer = csv.writer(outcsv, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
            writer.writerow(['GPUx2', 'GPUx3', 'GPUx4',  'GPUx5', 'GPUx6', 'GPUx7', 'GPUx8',])
            writer.writerow(traffics)        
        print(traffics) 
