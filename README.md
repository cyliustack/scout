# Introduction
SCOUT: A Multi-scale and Cross-framework Benchmarking for Neural Network Processing Engines.  
This benchmark suite will include t-bench, dt-bench, and p-bench. 
* t-bench is a modified TensorFlow official performance benchmark (https://github.com/tensorflow/benchmarks)
* dt-bench is a distributed CNN models training benchmark. Currently it is extension of t-bench. 
* p-bench is developed based on PyTorch examples. 
* s-bench is a TensorFlow.Keras distributed traing benchmarks, which utilize tensorflow.distribute.strategy. 

Authors: All contributors. 
# Prerequisite
1. tensorflow >= 1.14.0
2. If you want to use profiling tool SOFA, please download it from https://github.com/cyliustack/sofa.git
3. If you wnat to use benchmark with real data, 
   * a small subset of imagenet (TFRecords-only) can be downloaded from https://drive.google.com/open?id=1fhHzOLaNSYRNHo7noM159m2uSXFS5-wx
   * a small subset of imagenet (raw data only) can be downloaded from,  https://drive.google.com/open?id=11A5qflaLTf8wt_gnkZfABTSJ0BR7bCi7
4. Real data installation is described below (ramdisk mounting is optional to you):   
   ```
   mkdir /tmp/ramdisk
   chmod 777 /tmp/ramdisk
   mount -t tmpfs -o size=2G tmpfs /tmp/ramdisk/   
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
sudo sysctl -w vm.drop_caches=3 
./t-bench --model=resnet50  
./t-bench --model=resnet50 --num_gpus=2 --strategy="parameter_server" 
./t-bench.py --model=resnet50 --data_dir /tmp/ramdisk/dataset/imagenet 
./s-bench --model=resnet50 --strategy="parameter_server"
./tools/get_latency.py resnet50
./dt-bench parameter_server:resnet50
./dt-bench distributed_replicated:resnet50 --hierarchical_copy
./dt-bench distributed_all_reduce:resnet50 --all_reduce_spec=pscpu#2
cd dt-bench && ./run_strategy.sh mi ; cd - 
```

# Usage: Advanced Platform Profiling 
```
./tools/p2p-trace.py record --max_num_gpus=8
./tools/p2p-trace.py report
```
