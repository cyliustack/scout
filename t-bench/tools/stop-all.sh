#!/bin/bash
pssh -PH "192.168.0.100 192.168.0.101" pkill python
pssh -PH "192.168.0.100 192.168.0.101" nvidia-smi --query-gpu=memory.used,memory.total,utilization.gpu --format=csv
