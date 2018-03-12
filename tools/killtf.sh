ps aux | grep tf_cnn_benchmarks.py | awk {'print $2'} | xargs kill -9
