#!/usr/bin/env python3.6
import numpy as np
import csv
import json
import sys
import argparse
import multiprocessing as mp
import glob
import os
from functools import partial
import subprocess
from time import sleep, time

if __name__ == "__main__":
    model = 'alexnet'
    batch_size = 64
    print("Your Python version is %s.%s.%s" % sys.version_info[:3])
    if sys.version_info < (3, 6):
        print("But SOFA requires minimum version of Python 3.5.")
        quit()

    parser = argparse.ArgumentParser(description='SOFA')

    parser.add_argument(
        'model',
        type=str,
        nargs='?',
        metavar='<MODEL>')
    parser.add_argument('--batch_size', metavar='N', type=int, required=False, help='the batch size with which thte latency measurement will be conducted')

    args = parser.parse_args()

    if args.model is not None:
        model = args.model
    if args.batch_size is not None:
        batch_size = args.batch_size


    subprocess.call('rm time_report.txt',shell=True)
    num_batches = 100
    diff_steps =  100
    commands = []
    execution_times = []
    commands.append('./scout ct-bench '+ model + ' --num_batches=' + str(num_batches) + ' --batch_size=' + str(batch_size))
    commands.append('./scout ct-bench '+ model + ' --num_batches=' + str(num_batches+diff_steps) + ' --batch_size=' + str(batch_size))
    for command in commands:
        subprocess.call(
            '/usr/bin/time -v ' +
            command +
            ' 2>> time_report.txt',
            shell=True)
        if os.path.isfile('time_report.txt'):
            with open('time_report.txt') as f:
                lines = f.readlines()
                print("Lines of report = %d" % len(lines))
                for line in lines:
                    if line.find('Elapsed (wall clock)') != -1:
                        print(line)
                        munites = float(line.split()[7].split(':')[0])
                        seconds = float(line.split()[7].split(':')[1])
                        execution_time = munites * 60 + seconds
                        print('execution_time = %lf' % execution_time)
                        execution_times.append(execution_time)
    print(execution_times)
    print('Single-step latency = %lf' % ((execution_times[2]-execution_times[1])/diff_steps) )
#  1     Command being timed: "ls"
#  2     User time (seconds): 0.00
#  3     System time (seconds): 0.00
#  4     Percent of CPU this job got: 0%
#  5     Elapsed (wall clock) time (h:mm:ss or m:ss): 0:00.00_
