# Introduction
SCOUT: A Multi-scale and Cross-framework Benchmarking for Neural Network Processing Engines.  
This benchmark suite will include t-bench, j-bench, and f-bench. 
* t-bench is modified TensorFlow official performance benchmark (https://github.com/tensorflow/benchmarks)
* j-bench is modified CNN multiple models benchmark (https://github.com/jcjohnson/cnn-benchmarks)
* f-bench is modified Fathom benchmark (https://github.com/rdadolf/fathom)  

Authors: James Liu (cyliustack@gmail.com), Kevin Lyu (iamorangez@gmail.com), Ryan Wei (sjeemb@gmail.com)
# Prerequisite
1. If you want to use profiling tool SOFA, please download it from https://github.com/cyliustack/sofa.git
2. If you wnat to use benchmark with real data, a small subset of imagenet (TFRecords-only) can be downloaded from https://drive.google.com/open?id=1fhHzOLaNSYRNHo7noM159m2uSXFS5-wx ; a small subset of imagenet (raw data only) can be downloaded from,  https://drive.google.com/open?id=11A5qflaLTf8wt_gnkZfABTSJ0BR7bCi7       Real data installation is described below (ramdisk mounting is optional to you):
   ```
   mkdir -p /tmp/ramdisk/dataset
   tar xvf imagenet_smallset.tar.gz
   mv imagenet_smallset /tmp/ramdisk/dataset/imagenet
   ```

# Install
```
./tools/prepare.sh
```  

# Usages: Basic Benchmarking 
```
./scout t-bench resnet50
./scout t-bench resnet50_real
./tools/get_latency.py resnet50
./scout dt-bench ps:alexnet  
```

# Usage: Advanced Platform Profiling 
```
./tools/p2p-trace.py record --max_num_gpus=8
./tools/p2p-trace.py report
```
