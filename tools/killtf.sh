nvidia-smi | awk '$4=="C" {print $3}' | xargs kill -9 ; nvidia-smi
