#!/bin/bash
./multigpu-train.sh resnet152 64 1 "--variable_update=parameter_server --local_parameter_device=cpu --use_nccl=False --num_batches=100" 1>> tbench_resnet152.log
./multigpu-train.sh resnet152 64 2 "--variable_update=parameter_server --local_parameter_device=cpu --use_nccl=False --num_batches=100" 1>> tbench_resnet152.log
./multigpu-train.sh resnet152 64 4 "--variable_update=parameter_server --local_parameter_device=cpu --use_nccl=False --num_batches=100" 1>> tbench_resnet152.log
./multigpu-train.sh resnet152 64 8 "--variable_update=parameter_server --local_parameter_device=cpu --use_nccl=False --num_batches=100" 1>> tbench_resnet152.log

