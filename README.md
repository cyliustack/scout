# Introduction
SCOUT: A Multi-scale and Cross-framework Benchmarking for Neural Network Processing Engines.  
This benchmark suite will include t-bench, j-bench, and f-bench. 
* t-bench is modified TensorFlow official performance benchmark (https://github.com/tensorflow/benchmarks)
* j-bench is modified CNN multiple models benchmark (https://github.com/jcjohnson/cnn-benchmarks)
* f-bench is modified Fathom benchmark (https://github.com/rdadolf/fathom)  

Authors: Cheng-Yueh Liu (cyliustack@gmail.com) 
#

# Usage   
```
./scout tbench alexnet 32 4
./scout jbench alexnet 32
./scout fbench tensorflow seq2seq 
./scout fbench caffe2 seq2seq
```
