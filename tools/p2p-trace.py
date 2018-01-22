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

def traces_to_json(traces, path):
    if len(traces) == 0:
        print_warning("Empty traces!")
        return 
    
    with open(path, 'w') as f:
        for trace in traces:
            print_info("Dump %s to JSON file"%trace.name)    
            if len(trace.data) > 0:
                f.write(trace.name+" = ")
                trace.data.rename(columns={trace.x_field:'x', trace.y_field:'y'}, inplace=True)
                sofa_series = { "name": trace.title,
                                    "color": trace.color,
                                    "data": json.loads(trace.data.to_json(orient='records'))
                                    }
                json.dump(sofa_series, f)
                trace.data.rename(columns={'x':trace.x_field, 'y':trace.y_field}, inplace=True)
            f.write("\n\n")  
        
        f.write("sofa_traces = [ ")
        for trace in traces :
            if len(trace.data) > 0:
                f.write(trace.name+",")
        f.write(" ]")        

 
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Xring Modeling')
    parser.add_argument('--logdir', metavar="/path/to/logdir", type=str, required=False, 
                    help='path to the directory which contains log files')
    parser.add_argument('--max_num_gpus', metavar="N", type=int, required=False,
                    help='specify the maximum number of GPUs to model')
    parser.add_argument('--model', metavar="model_name", type=str, required=False,
                    help='specify a DNN model [alexnet|inception3|resnet50|vgg16] ')
    parser.add_argument('--metric', type=str, required=False, metavar='metric',
                    help='performance metric, like hotspot, memory pressure')
    parser.add_argument('command', type=str, nargs=1, metavar='command',
            help='specify a command: [record|report]')
 

    args = parser.parse_args()
    command = args.command[0]
        
    logdir = "./scoutlog"
    if args.logdir != None:
        logdir = args.logdir

    logfile = logdir+"/"+'p2ptrace.csv' 
    
    if args.max_num_gpus != None:
        max_num_gpus = args.max_num_gpus
    else:
        max_num_gpus = 8
    num_gpus = max_num_gpus


    if args.model != None:
        model = args.model
    else:
        model = 'vgg16'

    if command == 'record':
        os.system("mkdir -p %s" % logdir)
        os.system("rm %s/p2ptrace*.csv" % logdir)
        os.system("nvprof --print-gpu-trace --unified-memory-profiling per-process-device --profile-child-processes --csv --log-file %s/p2ptrace-%%p.csv ./scout t-bench %s --num_gpus=%d && mv %s/p2ptrace-*.csv %s/p2ptrace.csv" % (logdir, model, max_num_gpus, logdir, logdir ) )
        
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
        heatmap = np.zeros((max_num_gpus, max_num_gpus))  
        hosts_recv = {'1':0, '2':0, '3':0, '4':0, '5':0, '6':0, '7':0, '8':0}
        for i in range(len(df)):
            if  df.iloc[i,20] == '[CUDA memcpy PtoP]':
                r = int(df.iat[i,17])-1
                c = int(df.iat[i,19])-1
                heatmap[r][c] = heatmap[r][c] + 1
                #print("[P2P] From %d to %d" % ( df.iat[i,17], df.iat[i,19] ) )
        hm_p2p = heatmap.copy()
        print(hm_p2p)

        print('[HtoD Info]')
        heatmap = np.zeros((max_num_gpus, 1))  
        for i in range(len(df)):
            if df.iloc[i,20] == '[CUDA memcpy HtoD]':
                index = int(df.iat[i,14])-1
                heatmap[index] = heatmap[index] + 1
                #print("[H2D] From Host to %d" % ( df.iat[i,14] ) )
        hm_h2d = heatmap.copy()
        print(hm_h2d)

         
        print('[DtoH Info]')
        heatmap = np.zeros((max_num_gpus, 1)) 
        for i in range(len(df)):
            if df.iloc[i,20] == '[CUDA memcpy DtoH]':
                index = int(df.iat[i,14])-1
                heatmap[index] = heatmap[index] + 1
                #print("[D2H] From %d to Host" % ( df.iat[i,14] ) )
        hm_d2h = heatmap.copy()
        print(hm_d2h)

      
        #nodes = pd.DataFrame( data={'name': ['node1','node2','node3','node4'],  'group': [1,2,2,3]} )
        #links = pd.DataFrame( data={'source': [0,1], 'target':[2,2],  'weight': [1,3]} )
        nodes = []
        links = []
        nodes.append({'name': 'Host','group':'0'})
        for i in range(num_gpus): 
            nodes.append({'name': 'GPU%d'%i,'group':i/4+1})
            if hm_h2d[i] > np.max(hm_h2d)/2:
                links.append({'source': 0, 'target':i+1, 'weight':5})
            if hm_d2h[i] > np.max(hm_d2h)/2:
                links.append({'source': i+1, 'target':0, 'weight':5})
                  
        for i in range(num_gpus):
            for j in range(num_gpus):
                if hm_p2p[i][j] > np.max(hm_p2p)/2:
                    links.append({'source': i+1, 'target':j+1, 'weight':1}) 
        graph = { 'nodes': nodes, 'links': links }        

        with open('graphFile.json','w') as f:
            json.dump(graph,f)

#       {
#  "nodes":[
#        {"name":"node1","group":1},
#        {"name":"node2","group":2},
#        {"name":"node3","group":2},
#        {"name":"node4","group":3}
#    ],
#    "links":[
#        {"source":2,"target":1,"weight":1},
#        {"source":0,"target":2,"weight":3}
#    ]
#} 
        import networkx as nx
        import numpy as np
        import matplotlib.pyplot as plt
        import pylab
        
        G = nx.DiGraph()
 
        for i in range(num_gpus): 
            if hm_h2d[i] > np.max(hm_h2d)/2:
                G.add_edges_from([('H','G%d'%i)], weight=1)
            if hm_d2h[i] > np.max(hm_d2h)/2:
                G.add_edges_from([('G%d'%i,'H')], weight=1)
        for i in range(num_gpus):
            for j in range(num_gpus):
                if hm_p2p[i][j] > np.max(hm_p2p)/2:
                    G.add_edges_from([('G%d'%i,'G%d'%j)], weight=1)
        
#        G.add_edges_from([('G%d'%i,'G%d'%j), weight=1)
#        G.add_edges_from([('D','A'),('D','E'),('B','D'),('D','E')], weight=2)
#        G.add_edges_from([('B','C'),('E','F')], weight=3)
#        G.add_edges_from([('C','F')], weight=4)
#        
        
        val_map = {'A': 1.0,
                           'D': 0.5714285714285714,
                                      'H': 0.0}
        
        values = [val_map.get(node, 0.45) for node in G.nodes()]
        edge_labels=dict([((u,v,),d['weight'])
                         for u,v,d in G.edges(data=True)])
        red_edges = [('C','D'),('D','A')]
        edge_colors = ['black' if not edge in red_edges else 'red' for edge in G.edges()]
        
        pos=nx.spring_layout(G)
        nx.draw_networkx_edge_labels(G,pos,edge_labels=edge_labels)
        nx.draw(G,pos, node_color = values, node_size=1500,edge_color=edge_colors,edge_cmap=plt.cm.Reds)
        pylab.show()
        pylab.savefig("Graph.png", format="PNG")            
        
        os.system("cp graphFile.json %s"%logdir)
        os.system("cp tools/interconnection.html %s"%logdir)
        os.system("rm %s.tmp"%logfile)
