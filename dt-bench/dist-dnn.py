#!/usr/bin/python
import numpy as np
import csv
import json
import sys
import argparse
import multiprocessing as mp 
import subprocess
import glob, os 
from functools import partial

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    DATA = '\033[5;30;47m'
    TITLE = '\033[7;34;47m'
    C_NONE='\033[0;00m'
    C_RED='\033[1;31m'
    C_GREEN='\033[1;32m'

def print_title(content):
    print('\n')
    print(bcolors.TITLE  + content + bcolors.ENDC)

def print_error(content):
    print(bcolors.C_RED + "[ERROR] " + content + bcolors.ENDC)

def print_warning(content):
    print(bcolors.WARNING + "[WARNING] " + content + bcolors.ENDC)

def print_info(content):
    print(bcolors.OKGREEN + "[INFO] " + content + bcolors.ENDC)

def print_progress(content):
    print(bcolors.OKBLUE + "[INFO] " + content + bcolors.ENDC)


if __name__ == "__main__":
    
    logdir   = './scoutlog/' 
    sync = None
    model = None
    hostfile = 'hostfile.txt'
    sys.stdout.flush() 
 
    parser = argparse.ArgumentParser(description='DT-Bench')
    parser.add_argument('--logdir', metavar='/path/to/logdir/', type=str, required=False, 
                    help='path to the directory of dt-bench logged files')
    parser.add_argument('sync', type=str, nargs=1, metavar='<ps|replicated>')
    parser.add_argument('model', type=str, nargs=1, metavar='<alexnet|vgg16|resnet50>')

    args = parser.parse_args()
    if args.logdir != None:
        logdir = args.logdir + '/'
    
    if args.sync != None:
        sync = args.sync[0]
    if args.model != None:
        model = args.model[0]
    print_info("logdir = %s" % logdir )
    print_info("sync = %s" % sync )
    print_info("model = %s" % model )
    
    subprocess.call(['mkdir', '-p', logdir])
    with open('%s/scout.log'%logdir, 'w') as logfile:
        subprocess.call(['hostname'])
	#subprocess.call(['python', '../t-bench/scripts/tf_dnn_benchmarks/tf_benchmarkrs.py'])
