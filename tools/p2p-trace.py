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
    parser.add_argument('--logfile', metavar="/path/to/logfile", type=str, required=False, 
                    help='path to the profiling log files')
    parser.add_argument('--max_num_gpus', metavar="N", type=int, required=False,
                    help='specify the maximum number of GPUs to model')
    parser.add_argument('--model', metavar="model_name", type=str, required=False,
                    help='specify a DNN model [alexnet|inception3|resnet50|vgg16] ')
    parser.add_argument('--metric', type=str, required=False, metavar='metric',
                    help='performance metric, like hotspot, memory pressure')
    parser.add_argument('command', type=str, nargs=1, metavar='command',
            help='specify a command: [record|report]')
 
    logfile = 'p2ptrace.csv' 
    args = parser.parse_args()
    command = args.command[0]

    if args.logfile != None:
        logfile = args.logfile

    if args.max_num_gpus != None:
        max_num_gpus = args.max_num_gpus
    else:
        max_num_gpus = 8

    if args.model != None:
        model = args.model
    else:
        model = 'vgg16'

    if command == 'record':
        os.system("nvprof --print-gpu-trace --unified-memory-profiling per-process-device --profile-child-processes --csv --log-file p2ptrace-%%p.csv ./scout t-bench %s --num_gpus=%d && mv p2ptrace-*.csv p2ptrace.csv" % (model, max_num_gpus) )
        
    if command == 'report':
        df = []
        hosts=[]
        with open(logfile) as fin, open(logfile+'.tmp','w') as fout:
            lines = fin.readlines() 
            del lines[0]
            del lines[0]
            del lines[0]
            del lines[1]
            for line in lines:
                fout.write(line)

        with open(logfile+'.tmp') as f:
            df = pd.read_csv(f)
            print(df.columns)
            print(df.shape)
        
        print('[PtoP Info]')
        heatmap = np.zeros((8, 8))  
        hosts_recv = {'1':0, '2':0, '3':0, '4':0, '5':0, '6':0, '7':0, '8':0}
        for i in range(len(df)):
            if  df.iloc[i,20] == '[CUDA memcpy PtoP]':
                r = int(df.iat[i,17])-1
                c = int(df.iat[i,19])-1
                heatmap[r][c] = heatmap[r][c] + 1
                #print("[P2P] From %d to %d" % ( df.iat[i,17], df.iat[i,19] ) )
        print(heatmap)

        print('[HtoD Info]')
        heatmap = np.zeros((8, 1))  
        for i in range(len(df)):
            if df.iloc[i,20] == '[CUDA memcpy HtoD]':
                index = int(df.iat[i,14])-1
                heatmap[index] = heatmap[index] + 1
                #print("[H2D] From Host to %d" % ( df.iat[i,14] ) )
        print(heatmap)

         
        print('[DtoH Info]')
        heatmap = np.zeros((8, 1)) 
        for i in range(len(df)):
            if df.iloc[i,20] == '[CUDA memcpy DtoH]':
                index = int(df.iat[i,14])-1
                heatmap[index] = heatmap[index] + 1
                #print("[D2H] From %d to Host" % ( df.iat[i,14] ) )
        print(heatmap)
            
        os.system("rm p2ptrace*.tmp")
