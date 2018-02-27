# Introduction
SCOUT: A Multi-scale and Cross-framework Benchmarking for Neural Network Processing Engines.  
This benchmark suite will include t-bench, j-bench, and f-bench. 
* t-bench is modified TensorFlow official performance benchmark (https://github.com/tensorflow/benchmarks)
* j-bench is modified CNN multiple models benchmark (https://github.com/jcjohnson/cnn-benchmarks)
* f-bench is modified Fathom benchmark (https://github.com/rdadolf/fathom)  

Authors: James Liu (cyliustack@gmail.com),  Ryan Wei (sjeemb@gmail.com)   
# Prerequisite
If you want to use profiling tool SOFA, please download it from https://github.com/cyliustack/sofa.git   

# Install
```
./tools/prepare.sh
```  

# Usage: Basic Benchmarking 
```
./scout t-bench resnet50
./scout t-bench resnet50 --metric=sofa_standard
./scout j-bench alexnet
./scout f-bench seq2seq
./scout dt-bench ps:alexnet  
```

# Usage: Advanced Platform Profiling 
```
./tools/p2p-trace.py record --max_num_gpus=8
./tools/p2p-trace.py report
```
