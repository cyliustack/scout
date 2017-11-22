#!/bin/bash
# 1. Download cudnn-5.1
# 2. Download models.zip
# 3. mkdir models 
cd scout/j-bench
python tools/google_drive_download.py 0Byvt-AfX75o1STUxZTFpMU10djA models.zip
unzip models.zip
./run_cnn_benchmarks.py
