#!/bin/sh
python tf_cnn_benchmarks.py --local_parameter_device=cpu --num_gpus=2 \
--batch_size=32 --model=vgg16 --data_dir=/mnt/qnap/ImageNet_Dataset/imagenet-data \
--variable_update=parameter_server --nodistortions
